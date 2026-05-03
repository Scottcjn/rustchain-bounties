// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";

interface IBeacon {
    function getImplementation(address agent) external view returns (address);
    function verifyTrust(bytes32 trustHash, bytes calldata signature) external view returns (bool);
}

contract AgentFolioBeaconIntegration is Ownable, EIP712 {
    using ECDSA for bytes32;

    // --- Structs ---
    struct TrustProof {
        address agent;
        address beacon;
        uint256 timestamp;
        bytes32 trustRoot;
        bytes signature;
    }

    struct MigrationPath {
        address oldBeacon;
        address newBeacon;
        uint256 migrationDeadline;
        bool finalized;
    }

    // --- State ---
    mapping(address => address) public agentToBeacon; // agent => beacon
    mapping(address => MigrationPath) public migrationPaths;
    mapping(bytes32 => bool) public usedTrustProofs;

    // --- Events ---
    event AgentRegistered(address indexed agent, address indexed beacon, uint256 timestamp);
    event TrustVerified(address indexed agent, bytes32 trustHash, bool valid);
    event MigrationPathCreated(address indexed agent, address oldBeacon, address newBeacon, uint256 deadline);
    event MigrationFinalized(address indexed agent, address newBeacon);

    // --- Errors ---
    error InvalidSignature();
    error TrustProofAlreadyUsed();
    error MigrationExpired();
    error MigrationNotInitiated();
    error BeaconMismatch();

    // --- Constructor ---
    constructor() EIP712("AgentFolioBeaconIntegration", "1") Ownable(msg.sender) {}

    // --- Core Functions ---

    /// @notice Register an agent with its beacon
    function registerAgent(address agent, address beacon) external onlyOwner {
        require(beacon != address(0), "Invalid beacon");
        agentToBeacon[agent] = beacon;
        emit AgentRegistered(agent, beacon, block.timestamp);
    }

    /// @notice Verify trust proof from beacon
    function verifyTrust(TrustProof calldata proof) external returns (bool) {
        bytes32 trustHash = _hashTrustProof(proof);
        
        if (usedTrustProofs[trustHash]) revert TrustProofAlreadyUsed();
        
        address expectedBeacon = agentToBeacon[proof.agent];
        if (expectedBeacon != proof.beacon) revert BeaconMismatch();

        // Verify beacon signature
        bytes32 digest = _hashTypedDataV4(trustHash);
        address signer = ECDSA.recover(digest, proof.signature);
        
        if (signer != proof.beacon) revert InvalidSignature();

        usedTrustProofs[trustHash] = true;
        emit TrustVerified(proof.agent, trustHash, true);
        return true;
    }

    /// @notice Initiate migration path for agent
    function initiateMigration(
        address agent,
        address newBeacon,
        uint256 deadline
    ) external onlyOwner {
        require(newBeacon != address(0), "Invalid new beacon");
        require(deadline > block.timestamp, "Deadline must be in future");
        
        address oldBeacon = agentToBeacon[agent];
        require(oldBeacon != address(0), "Agent not registered");

        migrationPaths[agent] = MigrationPath({
            oldBeacon: oldBeacon,
            newBeacon: newBeacon,
            migrationDeadline: deadline,
            finalized: false
        });

        emit MigrationPathCreated(agent, oldBeacon, newBeacon, deadline);
    }

    /// @notice Finalize migration after deadline
    function finalizeMigration(address agent) external onlyOwner {
        MigrationPath storage path = migrationPaths[agent];
        
        if (path.migrationDeadline == 0) revert MigrationNotInitiated();
        if (block.timestamp < path.migrationDeadline) revert MigrationExpired();
        if (path.finalized) revert MigrationExpired();

        path.finalized = true;
        agentToBeacon[agent] = path.newBeacon;
        
        emit MigrationFinalized(agent, path.newBeacon);
    }

    /// @notice Get beacon implementation for agent
    function getBeaconImplementation(address agent) external view returns (address) {
        address beacon = agentToBeacon[agent];
        require(beacon != address(0), "Agent not registered");
        return IBeacon(beacon).getImplementation(agent);
    }

    // --- Internal Functions ---

    function _hashTrustProof(TrustProof calldata proof) internal pure returns (bytes32) {
        return keccak256(abi.encode(
            keccak256("TrustProof(address agent,address beacon,uint256 timestamp,bytes32 trustRoot)"),
            proof.agent,
            proof.beacon,
            proof.timestamp,
            proof.trustRoot
        ));
    }

    // --- Utility Functions ---

    /// @notice Check if trust proof is valid without consuming it
    function checkTrustProof(TrustProof calldata proof) external view returns (bool) {
        bytes32 trustHash = _hashTrustProof(proof);
        
        if (usedTrustProofs[trustHash]) return false;
        
        address expectedBeacon = agentToBeacon[proof.agent];
        if (expectedBeacon != proof.beacon) return false;

        bytes32 digest = _hashTypedDataV4(trustHash);
        address signer = ECDSA.recover(digest, proof.signature);
        
        return signer == proof.beacon;
    }

    /// @notice Get migration status for agent
    function getMigrationStatus(address agent) external view returns (MigrationPath memory) {
        return migrationPaths[agent];
    }
}