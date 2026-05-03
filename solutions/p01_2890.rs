// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";

interface IBeacon {
    function getImplementation(address _contract) external view returns (address);
    function upgradeTo(address _newImplementation) external;
}

interface IAgentFolio {
    function getAgent(address _agent) external view returns (Agent memory);
    function updateTrustScore(address _agent, uint256 _score) external;
    function migrateAgent(address _agent, address _newBeacon) external;
}

struct Agent {
    address agentAddress;
    uint256 trustScore;
    uint256 lastUpdated;
    bool isActive;
    bytes32 metadataHash;
}

contract AgentFolioBeaconBridge is Ownable, ReentrancyGuard, EIP712 {
    using ECDSA for bytes32;

    IERC20 public rtcToken;
    IBeacon public beacon;
    IAgentFolio public agentFolio;

    uint256 public constant MIN_TRUST_SCORE = 50;
    uint256 public constant MIGRATION_FEE = 100 * 10**18; // 100 RTC
    uint256 public constant BOUNTY_REWARD = 200 * 10**18; // 200 RTC

    mapping(address => bool) public migratedAgents;
    mapping(address => uint256) public pendingRewards;
    mapping(bytes32 => bool) public usedSignatures;

    event AgentMigrated(address indexed agent, address indexed newBeacon, uint256 timestamp);
    event TrustScoreUpdated(address indexed agent, uint256 newScore, uint256 timestamp);
    event RewardClaimed(address indexed claimer, uint256 amount, uint256 timestamp);
    event MigrationFeePaid(address indexed payer, uint256 amount, uint256 timestamp);

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

    function migrateAgent(
        address _agent,
        address _newBeacon,
        bytes calldata _signature
    ) external nonReentrant returns (bool) {
        require(!migratedAgents[_agent], "Agent already migrated");
        require(_agent != address(0), "Invalid agent address");
        require(_newBeacon != address(0), "Invalid new beacon");

        // Verify signature from AgentFolio
        bytes32 structHash = keccak256(abi.encode(
            keccak256("MigrateAgent(address agent,address newBeacon,uint256 nonce)"),
            _agent,
            _newBeacon,
            block.timestamp
        ));
        bytes32 digest = _hashTypedDataV4(structHash);
        address signer = ECDSA.recover(digest, _signature);
        require(signer == owner(), "Invalid signature");

        // Prevent replay attacks
        bytes32 signatureHash = keccak256(_signature);
        require(!usedSignatures[signatureHash], "Signature already used");
        usedSignatures[signatureHash] = true;

        // Verify trust score
        Agent memory agentData = agentFolio.getAgent(_agent);
        require(agentData.trustScore >= MIN_TRUST_SCORE, "Trust score too low");
        require(agentData.isActive, "Agent not active");

        // Pay migration fee
        require(
            rtcToken.transferFrom(msg.sender, address(this), MIGRATION_FEE),
            "Fee transfer failed"
        );
        emit MigrationFeePaid(msg.sender, MIGRATION_FEE, block.timestamp);

        // Perform migration
        agentFolio.migrateAgent(_agent, _newBeacon);
        migratedAgents[_agent] = true;

        // Calculate and store reward
        uint256 reward = calculateReward(agentData.trustScore);
        pendingRewards[msg.sender] += reward;

        emit AgentMigrated(_agent, _newBeacon, block.timestamp);
        return true;
    }

    function updateTrustScore(
        address _agent,
        uint256 _newScore,
        bytes calldata _signature
    ) external nonReentrant {
        require(migratedAgents[_agent], "Agent not migrated");
        require(_newScore <= 100, "Invalid score");

        // Verify signature from beacon
        bytes32 structHash = keccak256(abi.encode(
            keccak256("UpdateTrustScore(address agent,uint256 newScore,uint256 nonce)"),
            _agent,
            _newScore,
            block.timestamp
        ));
        bytes32 digest = _hashTypedDataV4(structHash);
        address signer = ECDSA.recover(digest, _signature);
        require(signer == address(beacon), "Invalid beacon signature");

        // Prevent replay attacks
        bytes32 signatureHash = keccak256(_signature);
        require(!usedSignatures[signatureHash], "Signature already used");
        usedSignatures[signatureHash] = true;

        // Update trust score on AgentFolio
        agentFolio.updateTrustScore(_agent, _newScore);

        emit TrustScoreUpdated(_agent, _newScore, block.timestamp);
    }

    function claimReward() external nonReentrant {
        uint256 reward = pendingRewards[msg.sender];
        require(reward > 0, "No pending rewards");

        pendingRewards[msg.sender] = 0;
        require(rtcToken.transfer(msg.sender, reward), "Reward transfer failed");

        emit RewardClaimed(msg.sender, reward, block.timestamp);
    }

    function calculateReward(uint256 _trustScore) public pure returns (uint256) {
        // Base reward + bonus for high trust scores
        uint256 baseReward = BOUNTY_REWARD;
        if (_trustScore >= 90) {
            return baseReward * 150 / 100; // 50% bonus
        } else if (_trustScore >= 75) {
            return baseReward * 125 / 100; // 25% bonus
        }
        return baseReward;
    }

    function verifyAgentMigration(
        address _agent,
        address _expectedBeacon
    ) external view returns (bool) {
        if (!migratedAgents[_agent]) return false;
        address currentImpl = beacon.getImplementation(_agent);
        return currentImpl == _expectedBeacon;
    }

    function getAgentStatus(address _agent) external view returns (
        bool isMigrated,
        uint256 trustScore,
        uint256 lastUpdated,
        bool isActive
    ) {
        isMigrated = migratedAgents[_agent];
        Agent memory agentData = agentFolio.getAgent(_agent);
        return (
            isMigrated,
            agentData.trustScore,
            agentData.lastUpdated,
            agentData.isActive
        );
    }

    function withdrawFees() external onlyOwner {
        uint256 balance = rtcToken.balanceOf(address(this));
        uint256 totalRewards = getTotalPendingRewards();
        uint256 withdrawable = balance - totalRewards;
        require(withdrawable > 0, "No withdrawable funds");
        require(rtcToken.transfer(owner(), withdrawable), "Withdraw failed");
    }

    function getTotalPendingRewards() public view returns (uint256) {
        // This would need a more efficient implementation in production
        return 0; // Placeholder
    }

    // Emergency functions
    function emergencyWithdraw() external onlyOwner {
        uint256 balance = rtcToken.balanceOf(address(this));
        require(balance > 0, "No balance");
        require(rtcToken.transfer(owner(), balance), "Emergency withdraw failed");
    }

    function updateBeacon(address _newBeacon) external onlyOwner {
        require(_newBeacon != address(0), "Invalid beacon");
        beacon = IBeacon(_newBeacon);
    }

    function updateAgentFolio(address _newAgentFolio) external onlyOwner {
        require(_newAgentFolio != address(0), "Invalid AgentFolio");
        agentFolio = IAgentFolio(_newAgentFolio);
    }
}