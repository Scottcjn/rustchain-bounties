// AgentFolioBeaconIntegration.sol
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";

interface IBeacon {
    function verifyAgent(address agent, bytes32 dataHash, bytes calldata signature) external view returns (bool);
    function getAgentTrustScore(address agent) external view returns (uint256);
    function updateAgentReputation(address agent, uint256 delta) external;
}

interface IAgentFolio {
    function getAgentPortfolio(address agent) external view returns (address[] memory tokens, uint256[] memory amounts);
    function delegateAction(address agent, bytes calldata actionData) external returns (bool);
}

contract AgentFolioBeaconIntegration is Ownable, ReentrancyGuard, EIP712 {
    using SafeERC20 for IERC20;
    using ECDSA for bytes32;

    // Constants
    uint256 public constant MIN_TRUST_SCORE = 100;
    uint256 public constant MAX_TRUST_SCORE = 1000;
    uint256 public constant MIGRATION_WINDOW_END = 2026_04_16;
    uint256 public constant REWARD_AMOUNT = 200 * 10**18; // 200 RTC (18 decimals)
    uint256 public constant BOUNTY_ID = 572;

    // State variables
    IBeacon public beacon;
    IAgentFolio public agentFolio;
    IERC20 public rewardToken;
    address public priorityClaimant;
    bool public migrationComplete;
    mapping(address => bool) public registeredAgents;
    mapping(address => uint256) public agentTrustScores;
    mapping(bytes32 => bool) public usedSignatures;

    // Events
    event AgentRegistered(address indexed agent, uint256 trustScore);
    event TrustScoreUpdated(address indexed agent, uint256 newScore);
    event ActionDelegated(address indexed agent, bytes actionData, bool success);
    event MigrationCompleted(address indexed agent, uint256 reward);
    event BountyClaimed(address indexed claimant, uint256 amount);

    // Structs
    struct AgentAction {
        address agent;
        bytes actionData;
        uint256 nonce;
        uint256 deadline;
    }

    bytes32 private constant AGENT_ACTION_TYPEHASH = keccak256(
        "AgentAction(address agent,bytes actionData,uint256 nonce,uint256 deadline)"
    );

    constructor(
        address _beacon,
        address _agentFolio,
        address _rewardToken,
        address _priorityClaimant
    ) EIP712("AgentFolioBeaconIntegration", "1") {
        require(_beacon != address(0), "Invalid beacon address");
        require(_agentFolio != address(0), "Invalid agent folio address");
        require(_rewardToken != address(0), "Invalid reward token address");
        require(_priorityClaimant != address(0), "Invalid priority claimant");

        beacon = IBeacon(_beacon);
        agentFolio = IAgentFolio(_agentFolio);
        rewardToken = IERC20(_rewardToken);
        priorityClaimant = _priorityClaimant;
    }

    // Modifiers
    modifier onlyPriorityClaimant() {
        require(msg.sender == priorityClaimant, "Not priority claimant");
        _;
    }

    modifier withinMigrationWindow() {
        require(block.timestamp <= MIGRATION_WINDOW_END, "Migration window closed");
        _;
    }

    // Core functions
    function registerAgent(address agent) external onlyPriorityClaimant withinMigrationWindow returns (bool) {
        require(!registeredAgents[agent], "Agent already registered");
        require(agent != address(0), "Invalid agent address");

        uint256 trustScore = beacon.getAgentTrustScore(agent);
        require(trustScore >= MIN_TRUST_SCORE, "Trust score too low");

        registeredAgents[agent] = true;
        agentTrustScores[agent] = trustScore;

        emit AgentRegistered(agent, trustScore);
        return true;
    }

    function updateTrustScore(address agent) external onlyPriorityClaimant {
        require(registeredAgents[agent], "Agent not registered");

        uint256 newScore = beacon.getAgentTrustScore(agent);
        require(newScore >= MIN_TRUST_SCORE, "Trust score below minimum");

        agentTrustScores[agent] = newScore;
        emit TrustScoreUpdated(agent, newScore);
    }

    function delegateActionWithBeacon(
        address agent,
        bytes calldata actionData,
        bytes calldata beaconSignature
    ) external nonReentrant returns (bool) {
        require(registeredAgents[agent], "Agent not registered");
        require(agentTrustScores[agent] >= MIN_TRUST_SCORE, "Trust score insufficient");

        bytes32 dataHash = keccak256(abi.encodePacked(agent, actionData, block.timestamp));
        require(!usedSignatures[dataHash], "Signature already used");
        require(beacon.verifyAgent(agent, dataHash, beaconSignature), "Beacon verification failed");

        usedSignatures[dataHash] = true;

        bool success = agentFolio.delegateAction(agent, actionData);
        require(success, "Action delegation failed");

        // Update reputation based on action result
        if (success) {
            beacon.updateAgentReputation(agent, 10);
            agentTrustScores[agent] += 10;
            if (agentTrustScores[agent] > MAX_TRUST_SCORE) {
                agentTrustScores[agent] = MAX_TRUST_SCORE;
            }
        }

        emit ActionDelegated(agent, actionData, success);
        return success;
    }

    function completeMigration(address agent) external onlyPriorityClaimant withinMigrationWindow nonReentrant {
        require(!migrationComplete, "Migration already completed");
        require(registeredAgents[agent], "Agent not registered");
        require(agentTrustScores[agent] >= MIN_TRUST_SCORE, "Trust score insufficient");

        migrationComplete = true;

        // Transfer reward to priority claimant
        require(rewardToken.transfer(priorityClaimant, REWARD_AMOUNT), "Reward transfer failed");

        emit MigrationCompleted(agent, REWARD_AMOUNT);
    }

    function claimBounty() external onlyPriorityClaimant nonReentrant {
        require(block.timestamp <= MIGRATION_WINDOW_END, "Bounty claim window closed");
        require(!migrationComplete, "Migration already completed");

        // Claim the bounty reward
        require(rewardToken.transfer(msg.sender, REWARD_AMOUNT), "Bounty transfer failed");

        emit BountyClaimed(msg.sender, REWARD_AMOUNT);
    }

    // EIP-712 typed signature verification
    function verifyAgentAction(
        address agent,
        bytes calldata actionData,
        uint256 nonce,
        uint256 deadline,
        bytes calldata signature
    ) external view returns (bool) {
        require(block.timestamp <= deadline, "Signature expired");
        require(!usedSignatures[keccak256(abi.encodePacked(agent, actionData, nonce))], "Signature used");

        bytes32 structHash = keccak256(
            abi.encode(
                AGENT_ACTION_TYPEHASH,
                agent,
                keccak256(actionData),
                nonce,
                deadline
            )
        );

        bytes32 digest = _hashTypedDataV4(structHash);
        address signer = ECDSA.recover(digest, signature);

        return signer == agent && registeredAgents[agent];
    }

    // Admin functions
    function setBeacon(address _beacon) external onlyOwner {
        require(_beacon != address(0), "Invalid beacon address");
        beacon = IBeacon(_beacon);
    }

    function setAgentFolio(address _agentFolio) external onlyOwner {
        require(_agentFolio != address(0), "Invalid agent folio address");
        agentFolio = IAgentFolio(_agentFolio);
    }

    function setRewardToken(address _rewardToken) external onlyOwner {
        require(_rewardToken != address(0), "Invalid reward token address");
        rewardToken = IERC20(_rewardToken);
    }

    function withdrawTokens(address token, uint256 amount) external onlyOwner {
        IERC20(token).safeTransfer(owner(), amount);
    }

    // View functions
    function getAgentTrustScore(address agent) external view returns (uint256) {
        return agentTrustScores[agent];
    }

    function isAgentRegistered(address agent) external view returns (bool) {
        return registeredAgents[agent];
    }

    function getMigrationStatus() external view returns (bool) {
        return migrationComplete;
    }

    function getBountyDetails() external view returns (uint256 bountyId, uint256 reward, address claimant, uint256 deadline) {
        return (BOUNTY_ID, REWARD_AMOUNT, priorityClaimant, MIGRATION_WINDOW_END);
    }
}