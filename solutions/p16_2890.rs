// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";

interface IBeacon {
    function verifyTrust(bytes32 agentId, bytes calldata signature) external view returns (bool);
    function getTrustScore(bytes32 agentId) external view returns (uint256);
    function registerAgent(bytes32 agentId, address agentAddress) external;
}

interface IAgentFolio {
    function getAgentProfile(bytes32 agentId) external view returns (AgentProfile memory);
    function updateTrustScore(bytes32 agentId, uint256 newScore) external;
    function isAgentActive(bytes32 agentId) external view returns (bool);
}

struct AgentProfile {
    bytes32 agentId;
    address agentAddress;
    string name;
    string metadataURI;
    uint256 trustScore;
    uint256 reputation;
    bool isActive;
    uint256 createdAt;
}

struct TrustEvidence {
    bytes32 agentId;
    address validator;
    uint256 score;
    bytes32 evidenceHash;
    uint256 timestamp;
    bytes signature;
}

contract AgentFolioBeaconBridge is Ownable, ReentrancyGuard, EIP712 {
    using ECDSA for bytes32;

    IBeacon public beacon;
    IAgentFolio public agentFolio;
    IERC20 public rewardToken;
    
    bytes32 private constant _TRUST_EVIDENCE_TYPEHASH = keccak256(
        "TrustEvidence(bytes32 agentId,address validator,uint256 score,bytes32 evidenceHash,uint256 timestamp)"
    );

    mapping(bytes32 => TrustEvidence[]) public trustHistory;
    mapping(bytes32 => uint256) public lastSyncTimestamp;
    mapping(address => bool) public authorizedValidators;
    mapping(bytes32 => bool) public processedEvidence;

    uint256 public constant MIN_TRUST_SCORE = 50;
    uint256 public constant MAX_TRUST_SCORE = 100;
    uint256 public constant SYNC_COOLDOWN = 1 hours;
    uint256 public constant REWARD_AMOUNT = 10 * 10**18; // 10 RTC tokens

    event AgentRegistered(bytes32 indexed agentId, address indexed agentAddress);
    event TrustScoreUpdated(bytes32 indexed agentId, uint256 oldScore, uint256 newScore);
    event EvidenceSubmitted(bytes32 indexed agentId, address indexed validator, uint256 score);
    event BridgeSynced(bytes32 indexed agentId, uint256 timestamp);
    event ValidatorAuthorized(address indexed validator);
    event ValidatorRevoked(address indexed validator);

    modifier onlyAuthorizedValidator() {
        require(authorizedValidators[msg.sender], "Not authorized validator");
        _;
    }

    modifier syncCooldown(bytes32 agentId) {
        require(
            block.timestamp >= lastSyncTimestamp[agentId] + SYNC_COOLDOWN,
            "Sync cooldown active"
        );
        _;
    }

    constructor(
        address _beacon,
        address _agentFolio,
        address _rewardToken
    ) EIP712("AgentFolioBeaconBridge", "1") {
        require(_beacon != address(0), "Invalid beacon address");
        require(_agentFolio != address(0), "Invalid agent folio address");
        require(_rewardToken != address(0), "Invalid reward token address");

        beacon = IBeacon(_beacon);
        agentFolio = IAgentFolio(_agentFolio);
        rewardToken = IERC20(_rewardToken);
    }

    function registerAgent(
        bytes32 agentId,
        address agentAddress,
        string calldata name,
        string calldata metadataURI
    ) external onlyOwner {
        require(!agentFolio.isAgentActive(agentId), "Agent already registered");
        
        beacon.registerAgent(agentId, agentAddress);
        
        emit AgentRegistered(agentId, agentAddress);
    }

    function submitTrustEvidence(
        bytes32 agentId,
        uint256 score,
        bytes32 evidenceHash,
        bytes calldata signature
    ) external onlyAuthorizedValidator nonReentrant {
        require(score >= MIN_TRUST_SCORE && score <= MAX_TRUST_SCORE, "Invalid score range");
        require(!processedEvidence[evidenceHash], "Evidence already processed");

        bytes32 structHash = keccak256(
            abi.encode(
                _TRUST_EVIDENCE_TYPEHASH,
                agentId,
                msg.sender,
                score,
                evidenceHash,
                block.timestamp
            )
        );

        bytes32 digest = _hashTypedDataV4(structHash);
        address signer = ECDSA.recover(digest, signature);
        require(signer == msg.sender, "Invalid signature");

        TrustEvidence memory evidence = TrustEvidence({
            agentId: agentId,
            validator: msg.sender,
            score: score,
            evidenceHash: evidenceHash,
            timestamp: block.timestamp,
            signature: signature
        });

        trustHistory[agentId].push(evidence);
        processedEvidence[evidenceHash] = true;

        // Update trust score in AgentFolio
        uint256 oldScore = agentFolio.getAgentProfile(agentId).trustScore;
        uint256 newScore = calculateWeightedScore(agentId, score);
        agentFolio.updateTrustScore(agentId, newScore);

        // Sync with Beacon
        syncWithBeacon(agentId);

        // Reward validator
        require(
            rewardToken.transfer(msg.sender, REWARD_AMOUNT),
            "Reward transfer failed"
        );

        emit EvidenceSubmitted(agentId, msg.sender, score);
        emit TrustScoreUpdated(agentId, oldScore, newScore);
    }

    function syncWithBeacon(bytes32 agentId) public syncCooldown(agentId) {
        require(agentFolio.isAgentActive(agentId), "Agent not active");
        
        AgentProfile memory profile = agentFolio.getAgentProfile(agentId);
        uint256 beaconScore = beacon.getTrustScore(agentId);
        
        // Merge trust scores using weighted average
        uint256 mergedScore = (profile.trustScore + beaconScore) / 2;
        
        agentFolio.updateTrustScore(agentId, mergedScore);
        lastSyncTimestamp[agentId] = block.timestamp;

        emit BridgeSynced(agentId, block.timestamp);
    }

    function calculateWeightedScore(bytes32 agentId, uint256 newEvidence) internal view returns (uint256) {
        TrustEvidence[] storage evidenceList = trustHistory[agentId];
        uint256 totalWeight = 0;
        uint256 weightedSum = 0;

        for (uint256 i = 0; i < evidenceList.length; i++) {
            uint256 age = block.timestamp - evidenceList[i].timestamp;
            uint256 weight = 1000 / (age + 1); // Recent evidence has more weight
            weightedSum += evidenceList[i].score * weight;
            totalWeight += weight;
        }

        // Include new evidence with maximum weight
        weightedSum += newEvidence * 1000;
        totalWeight += 1000;

        return weightedSum / totalWeight;
    }

    function authorizeValidator(address validator) external onlyOwner {
        require(validator != address(0), "Invalid validator address");
        authorizedValidators[validator] = true;
        emit ValidatorAuthorized(validator);
    }

    function revokeValidator(address validator) external onlyOwner {
        authorizedValidators[validator] = false;
        emit ValidatorRevoked(validator);
    }

    function getTrustHistory(bytes32 agentId) external view returns (TrustEvidence[] memory) {
        return trustHistory[agentId];
    }

    function getEvidenceCount(bytes32 agentId) external view returns (uint256) {
        return trustHistory[agentId].length;
    }

    function updateRewardAmount(uint256 newAmount) external onlyOwner {
        REWARD_AMOUNT = newAmount;
    }

    function updateSyncCooldown(uint256 newCooldown) external onlyOwner {
        SYNC_COOLDOWN = newCooldown;
    }

    function withdrawTokens(address token, uint256 amount) external onlyOwner {
        IERC20(token).transfer(owner(), amount);
    }
}