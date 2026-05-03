// AgentFolioBeaconIntegration.sol
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/draft-EIP712.sol";

interface IBeacon {
    function getBeaconData(bytes32 beaconId) external view returns (bytes memory);
    function verifyBeacon(bytes32 beaconId, bytes calldata signature) external view returns (bool);
}

interface IAgentFolio {
    function getAgentProfile(bytes32 agentId) external view returns (bytes memory);
    function verifyAgent(bytes32 agentId, bytes calldata signature) external view returns (bool);
}

contract AgentFolioBeaconIntegration is Ownable, ReentrancyGuard, EIP712 {
    using ECDSA for bytes32;

    // Structs
    struct TrustLink {
        bytes32 agentId;
        bytes32 beaconId;
        uint256 trustScore;
        uint256 timestamp;
        bool active;
    }

    struct MigrationRequest {
        bytes32 agentId;
        bytes32 beaconId;
        uint256 requestedTimestamp;
        bool processed;
    }

    // State variables
    IBeacon public beaconContract;
    IAgentFolio public agentFolioContract;
    IERC20 public rtcToken;
    
    mapping(bytes32 => TrustLink) public trustLinks;
    mapping(bytes32 => MigrationRequest) public migrationRequests;
    mapping(address => bool) public authorizedSigners;
    
    uint256 public constant TRUST_THRESHOLD = 70; // Minimum trust score (0-100)
    uint256 public constant MIGRATION_WINDOW = 7 days;
    uint256 public constant REWARD_AMOUNT = 200 * 10**18; // 200 RTC tokens
    
    bytes32 private constant _TRUST_LINK_TYPEHASH = keccak256("TrustLink(bytes32 agentId,bytes32 beaconId,uint256 trustScore,uint256 timestamp)");
    bytes32 private constant _MIGRATION_TYPEHASH = keccak256("MigrationRequest(bytes32 agentId,bytes32 beaconId,uint256 requestedTimestamp)");

    // Events
    event TrustLinkCreated(bytes32 indexed linkId, bytes32 agentId, bytes32 beaconId, uint256 trustScore);
    event TrustLinkUpdated(bytes32 indexed linkId, uint256 newTrustScore);
    event TrustLinkDeactivated(bytes32 indexed linkId);
    event MigrationRequested(bytes32 indexed requestId, bytes32 agentId, bytes32 beaconId);
    event MigrationProcessed(bytes32 indexed requestId, bytes32 agentId, bytes32 beaconId);
    event RewardClaimed(address indexed claimer, uint256 amount);

    // Modifiers
    modifier onlyAuthorizedSigner() {
        require(authorizedSigners[msg.sender], "Not authorized signer");
        _;
    }

    modifier validTrustLink(bytes32 linkId) {
        require(trustLinks[linkId].active, "Trust link not active");
        _;
    }

    // Constructor
    constructor(
        address _beaconContract,
        address _agentFolioContract,
        address _rtcToken
    ) EIP712("AgentFolioBeaconIntegration", "1") {
        beaconContract = IBeacon(_beaconContract);
        agentFolioContract = IAgentFolio(_agentFolioContract);
        rtcToken = IERC20(_rtcToken);
    }

    // Admin functions
    function setBeaconContract(address _beaconContract) external onlyOwner {
        beaconContract = IBeacon(_beaconContract);
    }

    function setAgentFolioContract(address _agentFolioContract) external onlyOwner {
        agentFolioContract = IAgentFolio(_agentFolioContract);
    }

    function setRtcToken(address _rtcToken) external onlyOwner {
        rtcToken = IERC20(_rtcToken);
    }

    function addAuthorizedSigner(address signer) external onlyOwner {
        authorizedSigners[signer] = true;
    }

    function removeAuthorizedSigner(address signer) external onlyOwner {
        authorizedSigners[signer] = false;
    }

    // Core functions
    function createTrustLink(
        bytes32 agentId,
        bytes32 beaconId,
        uint256 trustScore,
        bytes calldata agentSignature,
        bytes calldata beaconSignature
    ) external nonReentrant returns (bytes32) {
        require(trustScore <= 100, "Invalid trust score");
        require(trustScore >= TRUST_THRESHOLD, "Trust score below threshold");
        
        // Verify both parties
        require(agentFolioContract.verifyAgent(agentId, agentSignature), "Invalid agent signature");
        require(beaconContract.verifyBeacon(beaconId, beaconSignature), "Invalid beacon signature");
        
        bytes32 linkId = keccak256(abi.encodePacked(agentId, beaconId, block.timestamp));
        
        TrustLink memory newLink = TrustLink({
            agentId: agentId,
            beaconId: beaconId,
            trustScore: trustScore,
            timestamp: block.timestamp,
            active: true
        });
        
        trustLinks[linkId] = newLink;
        
        emit TrustLinkCreated(linkId, agentId, beaconId, trustScore);
        
        return linkId;
    }

    function updateTrustScore(
        bytes32 linkId,
        uint256 newTrustScore,
        bytes calldata signature
    ) external onlyAuthorizedSigner validTrustLink(linkId) {
        require(newTrustScore <= 100, "Invalid trust score");
        
        bytes32 digest = _hashTypedDataV4(keccak256(abi.encode(
            _TRUST_LINK_TYPEHASH,
            trustLinks[linkId].agentId,
            trustLinks[linkId].beaconId,
            newTrustScore,
            block.timestamp
        )));
        
        address signer = ECDSA.recover(digest, signature);
        require(authorizedSigners[signer], "Invalid signature");
        
        trustLinks[linkId].trustScore = newTrustScore;
        trustLinks[linkId].timestamp = block.timestamp;
        
        emit TrustLinkUpdated(linkId, newTrustScore);
    }

    function deactivateTrustLink(bytes32 linkId) external onlyAuthorizedSigner validTrustLink(linkId) {
        trustLinks[linkId].active = false;
        emit TrustLinkDeactivated(linkId);
    }

    function requestMigration(
        bytes32 agentId,
        bytes32 beaconId,
        bytes calldata signature
    ) external nonReentrant {
        bytes32 requestId = keccak256(abi.encodePacked(agentId, beaconId, block.timestamp));
        
        bytes32 digest = _hashTypedDataV4(keccak256(abi.encode(
            _MIGRATION_TYPEHASH,
            agentId,
            beaconId,
            block.timestamp
        )));
        
        address signer = ECDSA.recover(digest, signature);
        require(authorizedSigners[signer], "Invalid signature");
        
        MigrationRequest memory request = MigrationRequest({
            agentId: agentId,
            beaconId: beaconId,
            requestedTimestamp: block.timestamp,
            processed: false
        });
        
        migrationRequests[requestId] = request;
        
        emit MigrationRequested(requestId, agentId, beaconId);
    }

    function processMigration(bytes32 requestId) external onlyOwner nonReentrant {
        MigrationRequest storage request = migrationRequests[requestId];
        require(!request.processed, "Migration already processed");
        require(block.timestamp <= request.requestedTimestamp + MIGRATION_WINDOW, "Migration window expired");
        
        // Find and deactivate existing trust links
        bytes32 linkId = keccak256(abi.encodePacked(request.agentId, request.beaconId, request.requestedTimestamp));
        if (trustLinks[linkId].active) {
            trustLinks[linkId].active = false;
        }
        
        request.processed = true;
        
        emit MigrationProcessed(requestId, request.agentId, request.beaconId);
    }

    function claimReward(bytes32 requestId) external nonReentrant {
        MigrationRequest storage request = migrationRequests[requestId];
        require(request.processed, "Migration not processed");
        require(!_isRewardClaimed(requestId), "Reward already claimed");
        
        // Transfer RTC reward
        require(rtcToken.transfer(msg.sender, REWARD_AMOUNT), "Reward transfer failed");
        
        _markRewardClaimed(requestId);
        
        emit RewardClaimed(msg.sender, REWARD_AMOUNT);
    }

    // View functions
    function getTrustLink(bytes32 linkId) external view returns (TrustLink memory) {
        return trustLinks[linkId];
    }

    function getMigrationRequest(bytes32 requestId) external view returns (MigrationRequest memory) {
        return migrationRequests[requestId];
    }

    function verifyCrossLayerTrust(
        bytes32 agentId,
        bytes32 beaconId,
        bytes calldata agentData,
        bytes calldata beaconData
    ) external view returns (bool) {
        // Verify both layers independently
        bytes memory agentProfile = agentFolioContract.getAgentProfile(agentId);
        bytes memory beaconDataFromContract = beaconContract.getBeaconData(beaconId);
        
        // Compare provided data with on-chain data
        bool agentValid = keccak256(agentData) == keccak256(agentProfile);
        bool beaconValid = keccak256(beaconData) == keccak256(beaconDataFromContract);
        
        return agentValid && beaconValid;
    }

    // Internal functions
    function _isRewardClaimed(bytes32 requestId) internal view returns (bool) {
        // This would typically be stored in a mapping
        // For simplicity, we check if the request has been processed
        return migrationRequests[requestId].processed;
    }

    function _markRewardClaimed(bytes32 requestId) internal {
        // Mark reward as claimed (implementation depends on storage design)
        // For now, we just ensure the request is processed
        require(migrationRequests[requestId].processed, "Request not processed");
    }

    // Fallback
    receive() external payable {
        revert("Contract does not accept ETH");
    }
}