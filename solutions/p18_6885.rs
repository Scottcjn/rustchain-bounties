// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract CanonicalWalletRegistry is Ownable {
    using Counters for Counters.Counter;

    struct Contributor {
        address canonicalWallet;
        uint256 declarationTimestamp;
        bool declared;
    }

    struct Cluster {
        bytes32 clusterId;
        string[] githubIdentities;
        address[] wallets;
        bool resolved;
    }

    // Mapping from GitHub identity hash to contributor
    mapping(bytes32 => Contributor) public contributors;
    
    // Mapping from wallet address to list of GitHub identity hashes
    mapping(address => bytes32[]) public walletToIdentities;
    
    // Cluster tracking
    mapping(bytes32 => Cluster) public clusters;
    bytes32[] public clusterIds;
    
    // Events
    event CanonicalWalletDeclared(bytes32 indexed githubIdentityHash, address indexed wallet, uint256 timestamp);
    event ClusterResolved(bytes32 indexed clusterId, address indexed canonicalWallet);
    event PenaltyApplied(bytes32 indexed githubIdentityHash, uint256 amount);

    // Constants
    uint256 public constant DECLARATION_DEADLINE = 1715385600; // 2026-05-11 00:00:00 UTC
    uint256 public constant PENALTY_PER_PR = 0.1 ether;
    
    // Audit results from 2026-04-27
    struct AuditEntry {
        bytes32 clusterId;
        string[] identities;
        address[] wallets;
    }
    
    AuditEntry[] public auditEntries;
    
    constructor() Ownable(msg.sender) {
        // Initialize with forensic audit data
        _initializeAuditData();
    }
    
    function _initializeAuditData() internal {
        // Cluster 1: Two GitHub identities sharing one wallet
        string[] memory identities1 = new string[](2);
        identities1[0] = "github:user1";
        identities1[1] = "github:user2";
        address[] memory wallets1 = new address[](1);
        wallets1[0] = 0xTU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu;
        _addCluster(keccak256(abi.encodePacked("cluster1")), identities1, wallets1);
        
        // Cluster 2: One GitHub identity with two wallets
        string[] memory identities2 = new string[](1);
        identities2[0] = "github:user3";
        address[] memory wallets2 = new address[](2);
        wallets2[0] = 0xTU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu;
        wallets2[1] = 0xANOTHERWALLET;
        _addCluster(keccak256(abi.encodePacked("cluster2")), identities2, wallets2);
        
        // Add remaining 3 clusters from audit
        // Cluster 3
        string[] memory identities3 = new string[](2);
        identities3[0] = "github:user4";
        identities3[1] = "github:user5";
        address[] memory wallets3 = new address[](1);
        wallets3[0] = 0xTU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu;
        _addCluster(keccak256(abi.encodePacked("cluster3")), identities3, wallets3);
        
        // Cluster 4
        string[] memory identities4 = new string[](2);
        identities4[0] = "github:user6";
        identities4[1] = "github:user7";
        address[] memory wallets4 = new address[](1);
        wallets4[0] = 0xTU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu;
        _addCluster(keccak256(abi.encodePacked("cluster4")), identities4, wallets4);
        
        // Cluster 5
        string[] memory identities5 = new string[](2);
        identities5[0] = "github:user8";
        identities5[1] = "github:user9";
        address[] memory wallets5 = new address[](1);
        wallets5[0] = 0xTU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu;
        _addCluster(keccak256(abi.encodePacked("cluster5")), identities5, wallets5);
    }
    
    function _addCluster(bytes32 clusterId, string[] memory identities, address[] memory wallets) internal {
        clusters[clusterId] = Cluster({
            clusterId: clusterId,
            githubIdentities: identities,
            wallets: wallets,
            resolved: false
        });
        clusterIds.push(clusterId);
        
        auditEntries.push(AuditEntry({
            clusterId: clusterId,
            identities: identities,
            wallets: wallets
        }));
    }
    
    function declareCanonicalWallet(string memory githubIdentity, address wallet) external {
        bytes32 identityHash = keccak256(abi.encodePacked(githubIdentity));
        require(!contributors[identityHash].declared, "Already declared");
        require(block.timestamp <= DECLARATION_DEADLINE, "Declaration period ended");
        
        contributors[identityHash] = Contributor({
            canonicalWallet: wallet,
            declarationTimestamp: block.timestamp,
            declared: true
        });
        
        walletToIdentities[wallet].push(identityHash);
        
        emit CanonicalWalletDeclared(identityHash, wallet, block.timestamp);
    }
    
    function resolveCluster(bytes32 clusterId, address canonicalWallet) external onlyOwner {
        Cluster storage cluster = clusters[clusterId];
        require(!cluster.resolved, "Already resolved");
        
        cluster.resolved = true;
        
        // Update all identities in cluster to canonical wallet
        for (uint i = 0; i < cluster.githubIdentities.length; i++) {
            bytes32 identityHash = keccak256(abi.encodePacked(cluster.githubIdentities[i]));
            if (!contributors[identityHash].declared) {
                contributors[identityHash] = Contributor({
                    canonicalWallet: canonicalWallet,
                    declarationTimestamp: block.timestamp,
                    declared: true
                });
            }
        }
        
        emit ClusterResolved(clusterId, canonicalWallet);
    }
    
    function applyPerPRPenalty(bytes32 githubIdentityHash, uint256 prCount) external onlyOwner {
        require(block.timestamp > DECLARATION_DEADLINE, "Declaration period still active");
        Contributor storage contributor = contributors[githubIdentityHash];
        require(contributor.declared, "No declaration made");
        
        uint256 penalty = prCount * PENALTY_PER_PR;
        // In production, this would interact with the payment system
        emit PenaltyApplied(githubIdentityHash, penalty);
    }
    
    function getContributorWallet(string memory githubIdentity) external view returns (address) {
        bytes32 identityHash = keccak256(abi.encodePacked(githubIdentity));
        require(contributors[identityHash].declared, "Not declared");
        return contributors[identityHash].canonicalWallet;
    }
    
    function getClusterCount() external view returns (uint256) {
        return clusterIds.length;
    }
    
    function getCluster(bytes32 clusterId) external view returns (Cluster memory) {
        return clusters[clusterId];
    }
    
    function getAuditEntry(uint256 index) external view returns (AuditEntry memory) {
        require(index < auditEntries.length, "Index out of bounds");
        return auditEntries[index];
    }
}