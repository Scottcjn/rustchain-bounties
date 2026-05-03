// AgentFolioBeaconIntegration.sol
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";

interface IBeaconOracle {
    function getTrustScore(address agent) external view returns (uint256);
    function verifyAttestation(bytes32 attestationHash, bytes calldata signature) external view returns (bool);
}

interface IAgentFolioRegistry {
    function isRegisteredAgent(address agent) external view returns (bool);
    function getAgentMetadata(address agent) external view returns (string memory, uint256, bool);
}

contract AgentFolioBeaconIntegration is Ownable, ReentrancyGuard, EIP712 {
    using SafeERC20 for IERC20;
    using ECDSA for bytes32;

    // Constants
    uint256 public constant MIN_TRUST_SCORE = 70;
    uint256 public constant MIGRATION_WINDOW_END = 2026_04_16; // Unix timestamp
    uint256 public constant REWARD_AMOUNT = 200 * 10**18; // 200 RTC (18 decimals)
    address public constant RTC_TOKEN = 0x...; // Replace with actual RTC token address
    address public constant PRIORITY_CLAIMER = 0x...; // @0xbrainkid address

    // State variables
    IBeaconOracle public beaconOracle;
    IAgentFolioRegistry public agentFolioRegistry;
    IERC20 public rtcToken;

    mapping(bytes32 => bool) public processedAttestations;
    mapping(address => uint256) public agentRewards;
    mapping(address => bool) public migratedAgents;

    // Events
    event AgentMigrated(address indexed agent, bytes32 attestationHash, uint256 timestamp);
    event RewardClaimed(address indexed agent, uint256 amount);
    event TrustScoreUpdated(address indexed agent, uint256 newScore);
    event IntegrationInitialized(address beaconOracle, address agentFolioRegistry);

    // Errors
    error MigrationWindowClosed();
    error InvalidAttestation();
    error InsufficientTrustScore();
    error AgentNotRegistered();
    error AlreadyMigrated();
    error ClaimNotAuthorized();
    error TransferFailed();

    constructor(
        address _beaconOracle,
        address _agentFolioRegistry,
        address _rtcToken
    ) EIP712("AgentFolioBeaconIntegration", "1") Ownable() {
        require(_beaconOracle != address(0), "Invalid Beacon Oracle address");
        require(_agentFolioRegistry != address(0), "Invalid AgentFolio Registry address");
        require(_rtcToken != address(0), "Invalid RTC token address");

        beaconOracle = IBeaconOracle(_beaconOracle);
        agentFolioRegistry = IAgentFolioRegistry(_agentFolioRegistry);
        rtcToken = IERC20(_rtcToken);

        emit IntegrationInitialized(_beaconOracle, _agentFolioRegistry);
    }

    // Modifiers
    modifier withinMigrationWindow() {
        if (block.timestamp > MIGRATION_WINDOW_END) revert MigrationWindowClosed();
        _;
    }

    modifier onlyPriorityClaimer() {
        if (msg.sender != PRIORITY_CLAIMER) revert ClaimNotAuthorized();
        _;
    }

    // Core migration function
    function migrateAgent(
        address agent,
        bytes calldata attestationData,
        bytes calldata signature
    ) external nonReentrant withinMigrationWindow returns (bool) {
        // Verify agent is registered in AgentFolio
        if (!agentFolioRegistry.isRegisteredAgent(agent)) revert AgentNotRegistered();

        // Check if already migrated
        if (migratedAgents[agent]) revert AlreadyMigrated();

        // Compute attestation hash
        bytes32 attestationHash = keccak256(abi.encodePacked(
            agent,
            block.timestamp,
            attestationData
        ));

        // Verify attestation with Beacon Oracle
        if (!beaconOracle.verifyAttestation(attestationHash, signature)) revert InvalidAttestation();

        // Check trust score
        uint256 trustScore = beaconOracle.getTrustScore(agent);
        if (trustScore < MIN_TRUST_SCORE) revert InsufficientTrustScore();

        // Mark agent as migrated
        migratedAgents[agent] = true;

        // Calculate reward (proportional to trust score)
        uint256 reward = calculateReward(trustScore);
        agentRewards[agent] = reward;

        emit AgentMigrated(agent, attestationHash, block.timestamp);
        emit TrustScoreUpdated(agent, trustScore);

        return true;
    }

    // Claim reward function
    function claimReward() external nonReentrant {
        address agent = msg.sender;
        uint256 reward = agentRewards[agent];

        if (reward == 0) revert ClaimNotAuthorized();
        if (!migratedAgents[agent]) revert AgentNotRegistered();

        // Reset reward to prevent reentrancy
        agentRewards[agent] = 0;

        // Transfer RTC tokens
        bool success = rtcToken.transfer(agent, reward);
        if (!success) revert TransferFailed();

        emit RewardClaimed(agent, reward);
    }

    // Priority claim for @0xbrainkid
    function priorityClaimReward() external onlyPriorityClaimer nonReentrant {
        address agent = PRIORITY_CLAIMER;
        uint256 reward = agentRewards[agent];

        if (reward == 0) revert ClaimNotAuthorized();
        if (!migratedAgents[agent]) revert AgentNotRegistered();

        agentRewards[agent] = 0;

        bool success = rtcToken.transfer(agent, reward);
        if (!success) revert TransferFailed();

        emit RewardClaimed(agent, reward);
    }

    // Calculate reward based on trust score
    function calculateReward(uint256 trustScore) public pure returns (uint256) {
        // Base reward + bonus for high trust scores
        uint256 baseReward = REWARD_AMOUNT / 2; // 100 RTC base
        uint256 bonusMultiplier = (trustScore - MIN_TRUST_SCORE) * 10; // 10% per point above minimum
        uint256 bonus = (baseReward * bonusMultiplier) / 100;
        return baseReward + bonus;
    }

    // View functions
    function getAgentStatus(address agent) external view returns (
        bool isRegistered,
        bool isMigrated,
        uint256 trustScore,
        uint256 pendingReward
    ) {
        isRegistered = agentFolioRegistry.isRegisteredAgent(agent);
        isMigrated = migratedAgents[agent];
        trustScore = beaconOracle.getTrustScore(agent);
        pendingReward = agentRewards[agent];
    }

    function getAttestationHash(
        address agent,
        uint256 timestamp,
        bytes calldata attestationData
    ) external pure returns (bytes32) {
        return keccak256(abi.encodePacked(agent, timestamp, attestationData));
    }

    // Admin functions
    function updateBeaconOracle(address newOracle) external onlyOwner {
        require(newOracle != address(0), "Invalid address");
        beaconOracle = IBeaconOracle(newOracle);
    }

    function updateAgentFolioRegistry(address newRegistry) external onlyOwner {
        require(newRegistry != address(0), "Invalid address");
        agentFolioRegistry = IAgentFolioRegistry(newRegistry);
    }

    function emergencyWithdrawTokens(address token, address to, uint256 amount) external onlyOwner {
        IERC20(token).safeTransfer(to, amount);
    }

    // Fallback
    receive() external payable {
        revert("Contract does not accept ETH");
    }
}