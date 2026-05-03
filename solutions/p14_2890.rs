// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";

interface IBeacon {
    function getImplementation(address agent) external view returns (address);
    function upgradeTo(address newImplementation) external;
}

interface IAgentFolio {
    function getAgent(address agentId) external view returns (Agent memory);
    function verifyAgent(address agent, bytes memory signature) external view returns (bool);
}

struct Agent {
    address agentAddress;
    string metadataURI;
    uint256 stake;
    bool active;
    uint256 lastHeartbeat;
}

contract AgentFolioBeaconBridge is Ownable, ReentrancyGuard, EIP712 {
    using SafeERC20 for IERC20;
    using ECDSA for bytes32;

    // --- Constants ---
    bytes32 private constant _MIGRATION_TYPEHASH = keccak256("Migration(address agent,address newBeacon,uint256 nonce,uint256 deadline)");
    bytes32 private constant _HEARTBEAT_TYPEHASH = keccak256("Heartbeat(address agent,uint256 timestamp,uint256 nonce)");

    // --- State Variables ---
    IERC20 public rtcToken;
    IBeacon public beacon;
    IAgentFolio public agentFolio;

    mapping(address => bool) public registeredAgents;
    mapping(address => uint256) public agentNonces;
    mapping(address => uint256) public agentStakes;
    mapping(address => uint256) public lastHeartbeat;
    mapping(address => address) public agentBeaconMapping;

    uint256 public constant MIN_STAKE = 100 * 10**18; // 100 RTC
    uint256 public constant HEARTBEAT_INTERVAL = 1 hours;
    uint256 public constant MIGRATION_DEADLINE = 2026_04_16; // Unix timestamp

    // --- Events ---
    event AgentRegistered(address indexed agent, uint256 stake);
    event AgentMigrated(address indexed agent, address indexed newBeacon, uint256 timestamp);
    event HeartbeatReceived(address indexed agent, uint256 timestamp);
    event StakeWithdrawn(address indexed agent, uint256 amount);
    event BeaconUpdated(address indexed oldBeacon, address indexed newBeacon);

    // --- Modifiers ---
    modifier onlyRegisteredAgent() {
        require(registeredAgents[msg.sender], "Agent not registered");
        _;
    }

    modifier withinMigrationWindow() {
        require(block.timestamp <= MIGRATION_DEADLINE, "Migration window closed");
        _;
    }

    // --- Constructor ---
    constructor(
        address _rtcToken,
        address _beacon,
        address _agentFolio
    ) EIP712("AgentFolioBeaconBridge", "1") {
        require(_rtcToken != address(0), "Invalid RTC token");
        require(_beacon != address(0), "Invalid beacon");
        require(_agentFolio != address(0), "Invalid AgentFolio");

        rtcToken = IERC20(_rtcToken);
        beacon = IBeacon(_beacon);
        agentFolio = IAgentFolio(_agentFolio);
    }

    // --- Registration Functions ---
    function registerAgent(bytes memory signature) external nonReentrant {
        require(!registeredAgents[msg.sender], "Already registered");
        require(agentFolio.verifyAgent(msg.sender, signature), "Agent verification failed");

        Agent memory agent = agentFolio.getAgent(msg.sender);
        require(agent.active, "Agent not active in AgentFolio");

        rtcToken.safeTransferFrom(msg.sender, address(this), MIN_STAKE);
        registeredAgents[msg.sender] = true;
        agentStakes[msg.sender] = MIN_STAKE;
        lastHeartbeat[msg.sender] = block.timestamp;

        emit AgentRegistered(msg.sender, MIN_STAKE);
    }

    // --- Migration Functions ---
    function migrateToBeacon(
        address newBeacon,
        uint256 deadline,
        bytes memory signature
    ) external onlyRegisteredAgent withinMigrationWindow nonReentrant {
        require(deadline >= block.timestamp, "Signature expired");
        require(newBeacon != address(0), "Invalid beacon address");

        bytes32 structHash = keccak256(
            abi.encode(
                _MIGRATION_TYPEHASH,
                msg.sender,
                newBeacon,
                agentNonces[msg.sender],
                deadline
            )
        );

        bytes32 digest = _hashTypedDataV4(structHash);
        address signer = ECDSA.recover(digest, signature);
        require(signer == owner(), "Invalid migration signature");

        agentNonces[msg.sender]++;

        // Perform migration
        address oldBeacon = agentBeaconMapping[msg.sender];
        agentBeaconMapping[msg.sender] = newBeacon;

        // Upgrade beacon implementation for this agent
        beacon.upgradeTo(newBeacon);

        emit AgentMigrated(msg.sender, newBeacon, block.timestamp);
    }

    // --- Heartbeat Functions ---
    function sendHeartbeat(bytes memory signature) external onlyRegisteredAgent {
        require(
            block.timestamp >= lastHeartbeat[msg.sender] + HEARTBEAT_INTERVAL,
            "Heartbeat too soon"
        );

        bytes32 structHash = keccak256(
            abi.encode(
                _HEARTBEAT_TYPEHASH,
                msg.sender,
                block.timestamp,
                agentNonces[msg.sender]
            )
        );

        bytes32 digest = _hashTypedDataV4(structHash);
        address signer = ECDSA.recover(digest, signature);
        require(signer == msg.sender, "Invalid heartbeat signature");

        agentNonces[msg.sender]++;
        lastHeartbeat[msg.sender] = block.timestamp;

        emit HeartbeatReceived(msg.sender, block.timestamp);
    }

    // --- Stake Management ---
    function withdrawStake() external onlyRegisteredAgent nonReentrant {
        require(
            block.timestamp >= lastHeartbeat[msg.sender] + HEARTBEAT_INTERVAL * 24,
            "Must miss 24 heartbeats to withdraw"
        );

        uint256 stake = agentStakes[msg.sender];
        require(stake > 0, "No stake to withdraw");

        agentStakes[msg.sender] = 0;
        registeredAgents[msg.sender] = false;

        rtcToken.safeTransfer(msg.sender, stake);

        emit StakeWithdrawn(msg.sender, stake);
    }

    // --- Admin Functions ---
    function updateBeacon(address newBeacon) external onlyOwner {
        require(newBeacon != address(0), "Invalid beacon");
        address oldBeacon = address(beacon);
        beacon = IBeacon(newBeacon);
        emit BeaconUpdated(oldBeacon, newBeacon);
    }

    function emergencyWithdraw(address token, uint256 amount) external onlyOwner {
        IERC20(token).safeTransfer(owner(), amount);
    }

    // --- View Functions ---
    function getAgentInfo(address agent) external view returns (
        bool registered,
        uint256 stake,
        uint256 lastHeartbeatTime,
        address currentBeacon,
        uint256 nonce
    ) {
        return (
            registeredAgents[agent],
            agentStakes[agent],
            lastHeartbeat[agent],
            agentBeaconMapping[agent],
            agentNonces[agent]
        );
    }

    function isAgentActive(address agent) external view returns (bool) {
        if (!registeredAgents[agent]) return false;
        return block.timestamp <= lastHeartbeat[agent] + HEARTBEAT_INTERVAL * 3;
    }

    // --- Receive Function ---
    receive() external payable {
        revert("Contract does not accept ETH");
    }
}