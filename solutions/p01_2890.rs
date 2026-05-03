// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";

interface IBeacon {
    function getImplementation(address _contract) external view returns (address);
    function verifyTrust(bytes32 _trustHash, bytes calldata _signature) external view returns (bool);
}

interface IAgentFolio {
    function getAgent(address _agent) external view returns (Agent memory);
    function verifyAgent(address _agent, bytes32 _dataHash, bytes calldata _signature) external view returns (bool);
}

struct Agent {
    address agentAddress;
    string name;
    string metadataURI;
    uint256 reputation;
    bool isActive;
}

struct TrustProof {
    bytes32 trustHash;
    bytes signature;
    uint256 timestamp;
    address issuer;
    address subject;
}

contract AgentFolioBeaconBridge is Ownable, ReentrancyGuard, EIP712 {
    using ECDSA for bytes32;

    // Events
    event TrustEstablished(address indexed agent, address indexed beacon, bytes32 trustHash, uint256 timestamp);
    event TrustRevoked(address indexed agent, address indexed beacon, bytes32 trustHash, uint256 timestamp);
    event MigrationCompleted(address indexed agent, address indexed oldBeacon, address indexed newBeacon, uint256 timestamp);
    event ReputationSynced(address indexed agent, uint256 oldReputation, uint256 newReputation, uint256 timestamp);

    // State variables
    IAgentFolio public agentFolio;
    IBeacon public beacon;
    
    mapping(address => mapping(address => TrustProof)) public agentTrustProofs; // agent => beacon => proof
    mapping(address => uint256) public agentReputationCache;
    mapping(address => bool) public migratedAgents;
    
    bytes32 private constant _TRUST_TYPEHASH = keccak256("TrustProof(address issuer,address subject,uint256 timestamp)");
    
    // Migration window
    uint256 public migrationDeadline;
    uint256 public constant MIGRATION_WINDOW = 7 days;
    
    // RTC token for rewards
    IERC20 public rtcToken;
    uint256 public constant BOUNTY_AMOUNT = 100 * 10**18; // 100 RTC

    constructor(
        address _agentFolio,
        address _beacon,
        address _rtcToken
    ) EIP712("AgentFolioBeaconBridge", "1") {
        agentFolio = IAgentFolio(_agentFolio);
        beacon = IBeacon(_beacon);
        rtcToken = IERC20(_rtcToken);
        migrationDeadline = block.timestamp + MIGRATION_WINDOW;
    }

    // Core trust establishment
    function establishTrust(
        address _agent,
        bytes32 _trustHash,
        bytes calldata _signature
    ) external nonReentrant {
        require(_agent != address(0), "Invalid agent address");
        require(agentFolio.getAgent(_agent).isActive, "Agent not active");
        require(beacon.verifyTrust(_trustHash, _signature), "Invalid trust proof");
        
        TrustProof memory proof = TrustProof({
            trustHash: _trustHash,
            signature: _signature,
            timestamp: block.timestamp,
            issuer: msg.sender,
            subject: _agent
        });
        
        agentTrustProofs[_agent][address(beacon)] = proof;
        
        // Sync reputation
        uint256 oldRep = agentReputationCache[_agent];
        uint256 newRep = agentFolio.getAgent(_agent).reputation;
        agentReputationCache[_agent] = newRep;
        
        emit TrustEstablished(_agent, address(beacon), _trustHash, block.timestamp);
        if (oldRep != newRep) {
            emit ReputationSynced(_agent, oldRep, newRep, block.timestamp);
        }
    }

    // Revoke trust
    function revokeTrust(address _agent) external nonReentrant {
        require(agentTrustProofs[_agent][address(beacon)].issuer == msg.sender, "Not trust issuer");
        
        bytes32 trustHash = agentTrustProofs[_agent][address(beacon)].trustHash;
        delete agentTrustProofs[_agent][address(beacon)];
        
        emit TrustRevoked(_agent, address(beacon), trustHash, block.timestamp);
    }

    // Migration from old beacon to new beacon
    function migrateToNewBeacon(
        address _agent,
        address _newBeacon,
        bytes32 _newTrustHash,
        bytes calldata _newSignature
    ) external nonReentrant {
        require(block.timestamp <= migrationDeadline, "Migration window closed");
        require(!migratedAgents[_agent], "Already migrated");
        require(_newBeacon != address(0), "Invalid new beacon");
        require(agentFolio.getAgent(_agent).isActive, "Agent not active");
        
        // Verify old trust exists
        require(agentTrustProofs[_agent][address(beacon)].timestamp > 0, "No existing trust");
        
        // Verify new beacon trust
        require(IBeacon(_newBeacon).verifyTrust(_newTrustHash, _newSignature), "Invalid new trust proof");
        
        // Transfer trust
        TrustProof memory newProof = TrustProof({
            trustHash: _newTrustHash,
            signature: _newSignature,
            timestamp: block.timestamp,
            issuer: msg.sender,
            subject: _agent
        });
        
        agentTrustProofs[_agent][_newBeacon] = newProof;
        migratedAgents[_agent] = true;
        
        // Clear old trust
        delete agentTrustProofs[_agent][address(beacon)];
        
        emit MigrationCompleted(_agent, address(beacon), _newBeacon, block.timestamp);
    }

    // Verify dual-layer trust
    function verifyDualTrust(
        address _agent,
        bytes32 _dataHash,
        bytes calldata _agentSignature,
        bytes32 _trustHash,
        bytes calldata _beaconSignature
    ) external view returns (bool) {
        // Layer 1: Agent verification
        bool agentVerified = agentFolio.verifyAgent(_agent, _dataHash, _agentSignature);
        
        // Layer 2: Beacon trust verification
        bool beaconVerified = beacon.verifyTrust(_trustHash, _beaconSignature);
        
        // Check trust proof exists
        bool trustExists = agentTrustProofs[_agent][address(beacon)].timestamp > 0;
        
        return agentVerified && beaconVerified && trustExists;
    }

    // Get trust proof for an agent
    function getTrustProof(address _agent) external view returns (TrustProof memory) {
        return agentTrustProofs[_agent][address(beacon)];
    }

    // Get cached reputation
    function getCachedReputation(address _agent) external view returns (uint256) {
        return agentReputationCache[_agent];
    }

    // Update reputation cache
    function syncReputation(address _agent) external {
        uint256 oldRep = agentReputationCache[_agent];
        uint256 newRep = agentFolio.getAgent(_agent).reputation;
        agentReputationCache[_agent] = newRep;
        
        emit ReputationSynced(_agent, oldRep, newRep, block.timestamp);
    }

    // Claim bounty reward
    function claimBounty() external nonReentrant {
        require(rtcToken.balanceOf(address(this)) >= BOUNTY_AMOUNT, "Insufficient bounty funds");
        require(rtcToken.transfer(msg.sender, BOUNTY_AMOUNT), "Transfer failed");
    }

    // Admin functions
    function setAgentFolio(address _newAgentFolio) external onlyOwner {
        agentFolio = IAgentFolio(_newAgentFolio);
    }

    function setBeacon(address _newBeacon) external onlyOwner {
        beacon = IBeacon(_newBeacon);
    }

    function setRtcToken(address _newRtcToken) external onlyOwner {
        rtcToken = IERC20(_newRtcToken);
    }

    function extendMigrationWindow(uint256 _additionalDays) external onlyOwner {
        migrationDeadline += _additionalDays * 1 days;
    }

    // Fund contract with RTC for bounties
    function fundBounty(uint256 _amount) external {
        require(rtcToken.transferFrom(msg.sender, address(this), _amount), "Transfer failed");
    }

    // Withdraw remaining RTC
    function withdrawRTC() external onlyOwner {
        uint256 balance = rtcToken.balanceOf(address(this));
        require(rtcToken.transfer(owner(), balance), "Transfer failed");
    }
}