// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

interface IBeacon {
    function getImplementation(address _agent) external view returns (address);
    function verifyTrust(address _agent, bytes32 _trustRoot) external view returns (bool);
}

interface IAgentFolio {
    function getAgent(address _agent) external view returns (Agent memory);
    function isActive(address _agent) external view returns (bool);
}

struct Agent {
    address agentAddress;
    bytes32 trustRoot;
    uint256 stake;
    uint256 reputation;
    bool active;
}

contract AgentFolioBeaconBridge is Ownable, ReentrancyGuard {
    using ECDSA for bytes32;

    IBeacon public beacon;
    IAgentFolio public agentFolio;
    IERC20 public rtcToken;

    mapping(address => bytes32) public agentTrustRoots;
    mapping(address => uint256) public agentStakes;
    mapping(address => uint256) public lastSyncTime;

    uint256 public constant MIN_STAKE = 100 * 10**18; // 100 RTC
    uint256 public constant SYNC_INTERVAL = 1 hours;
    uint256 public constant REPUTATION_BOOST = 10;

    event AgentRegistered(address indexed agent, bytes32 trustRoot, uint256 stake);
    event TrustRootUpdated(address indexed agent, bytes32 oldRoot, bytes32 newRoot);
    event StakeIncreased(address indexed agent, uint256 additionalStake);
    event StakeWithdrawn(address indexed agent, uint256 amount);
    event ReputationUpdated(address indexed agent, uint256 newReputation);
    event SyncCompleted(address indexed agent, uint256 timestamp);

    constructor(address _beacon, address _agentFolio, address _rtcToken) {
        require(_beacon != address(0), "Invalid beacon address");
        require(_agentFolio != address(0), "Invalid agent folio address");
        require(_rtcToken != address(0), "Invalid RTC token address");

        beacon = IBeacon(_beacon);
        agentFolio = IAgentFolio(_agentFolio);
        rtcToken = IERC20(_rtcToken);
    }

    modifier onlyActiveAgent(address _agent) {
        require(agentFolio.isActive(_agent), "Agent not active in AgentFolio");
        _;
    }

    modifier syncRequired(address _agent) {
        require(
            block.timestamp >= lastSyncTime[_agent] + SYNC_INTERVAL,
            "Sync not required yet"
        );
        _;
    }

    function registerAgent(bytes32 _trustRoot) external nonReentrant {
        address agent = msg.sender;
        require(agentTrustRoots[agent] == bytes32(0), "Agent already registered");
        require(rtcToken.transferFrom(agent, address(this), MIN_STAKE), "Stake transfer failed");

        agentTrustRoots[agent] = _trustRoot;
        agentStakes[agent] = MIN_STAKE;
        lastSyncTime[agent] = block.timestamp;

        emit AgentRegistered(agent, _trustRoot, MIN_STAKE);
    }

    function updateTrustRoot(bytes32 _newTrustRoot) external onlyActiveAgent(msg.sender) {
        address agent = msg.sender;
        bytes32 oldRoot = agentTrustRoots[agent];
        require(oldRoot != bytes32(0), "Agent not registered");
        require(_newTrustRoot != oldRoot, "New root same as old");

        agentTrustRoots[agent] = _newTrustRoot;
        emit TrustRootUpdated(agent, oldRoot, _newTrustRoot);
    }

    function increaseStake(uint256 _amount) external nonReentrant onlyActiveAgent(msg.sender) {
        require(_amount > 0, "Amount must be positive");
        require(rtcToken.transferFrom(msg.sender, address(this), _amount), "Transfer failed");

        agentStakes[msg.sender] += _amount;
        emit StakeIncreased(msg.sender, _amount);
    }

    function withdrawStake(uint256 _amount) external nonReentrant onlyActiveAgent(msg.sender) {
        address agent = msg.sender;
        require(_amount > 0, "Amount must be positive");
        require(agentStakes[agent] - _amount >= MIN_STAKE, "Cannot withdraw below minimum stake");

        agentStakes[agent] -= _amount;
        require(rtcToken.transfer(agent, _amount), "Withdrawal failed");

        emit StakeWithdrawn(agent, _amount);
    }

    function syncWithBeacon(address _agent) external syncRequired(_agent) nonReentrant {
        require(agentTrustRoots[_agent] != bytes32(0), "Agent not registered");

        bool beaconTrust = beacon.verifyTrust(_agent, agentTrustRoots[_agent]);
        bool folioActive = agentFolio.isActive(_agent);

        if (beaconTrust && folioActive) {
            // Update reputation in AgentFolio
            Agent memory agentData = agentFolio.getAgent(_agent);
            uint256 newReputation = agentData.reputation + REPUTATION_BOOST;
            emit ReputationUpdated(_agent, newReputation);
        }

        lastSyncTime[_agent] = block.timestamp;
        emit SyncCompleted(_agent, block.timestamp);
    }

    function verifyDualTrust(address _agent) external view returns (bool) {
        bytes32 trustRoot = agentTrustRoots[_agent];
        if (trustRoot == bytes32(0)) return false;

        bool beaconTrust = beacon.verifyTrust(_agent, trustRoot);
        bool folioActive = agentFolio.isActive(_agent);

        return beaconTrust && folioActive;
    }

    function getAgentInfo(address _agent) external view returns (
        bytes32 trustRoot,
        uint256 stake,
        uint256 lastSync,
        bool isRegistered
    ) {
        trustRoot = agentTrustRoots[_agent];
        stake = agentStakes[_agent];
        lastSync = lastSyncTime[_agent];
        isRegistered = trustRoot != bytes32(0);
    }

    function emergencyWithdraw() external onlyOwner {
        uint256 balance = rtcToken.balanceOf(address(this));
        require(balance > 0, "No balance to withdraw");
        require(rtcToken.transfer(owner(), balance), "Transfer failed");
    }

    function updateBeacon(address _newBeacon) external onlyOwner {
        require(_newBeacon != address(0), "Invalid address");
        beacon = IBeacon(_newBeacon);
    }

    function updateAgentFolio(address _newAgentFolio) external onlyOwner {
        require(_newAgentFolio != address(0), "Invalid address");
        agentFolio = IAgentFolio(_newAgentFolio);
    }
}