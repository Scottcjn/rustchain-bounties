// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";

contract CanonicalWalletRegistry is Ownable {
    using Counters for Counters.Counter;
    using EnumerableSet for EnumerableSet.AddressSet;
    using EnumerableSet for EnumerableSet.Bytes32Set;

    // --- Structs ---
    struct ContributorIdentity {
        bytes32 githubId;           // keccak256 of GitHub username
        address canonicalWallet;    // single RTC wallet
        uint256 declarationTimestamp;
        bool isActive;
    }

    struct WalletCluster {
        address wallet;
        bytes32[] associatedGithubIds;
        uint256 clusterSize;
    }

    // --- State ---
    mapping(bytes32 => ContributorIdentity) public identities;        // githubId => identity
    mapping(address => EnumerableSet.Bytes32Set) private walletToGithubIds; // wallet => set of githubIds
    EnumerableSet.Bytes32Set private allGithubIds;
    EnumerableSet.AddressSet private allWallets;

    // Audit results
    WalletCluster[] public auditClusters;
    mapping(bytes32 => bool) public flaggedIdentities;
    uint256 public auditTimestamp;
    uint256 public declarationDeadline;

    // Events
    event CanonicalWalletDeclared(bytes32 indexed githubId, address indexed wallet, uint256 timestamp);
    event IdentityFlagged(bytes32 indexed githubId, address indexed wallet, string reason);
    event ClusterResolved(bytes32 indexed githubId, address indexed oldWallet, address indexed newWallet);

    // --- Constructor ---
    constructor(uint256 _declarationDeadline) Ownable(msg.sender) {
        declarationDeadline = _declarationDeadline;
    }

    // --- Modifiers ---
    modifier onlyBeforeDeadline() {
        require(block.timestamp <= declarationDeadline, "Declaration deadline passed");
        _;
    }

    modifier onlyAfterAudit() {
        require(auditTimestamp > 0, "Audit not yet performed");
        _;
    }

    // --- Admin Functions ---
    function performAudit(WalletCluster[] calldata clusters) external onlyOwner {
        require(auditTimestamp == 0, "Audit already performed");
        auditTimestamp = block.timestamp;

        for (uint256 i = 0; i < clusters.length; i++) {
            auditClusters.push(clusters[i]);
            for (uint256 j = 0; j < clusters[i].associatedGithubIds.length; j++) {
                flaggedIdentities[clusters[i].associatedGithubIds[j]] = true;
                emit IdentityFlagged(
                    clusters[i].associatedGithubIds[j],
                    clusters[i].wallet,
                    "Multiple identities sharing wallet"
                );
            }
        }
    }

    // --- Core Logic ---
    function declareCanonicalWallet(bytes32 githubId, address wallet) external onlyBeforeDeadline {
        require(wallet != address(0), "Invalid wallet address");
        require(githubId != bytes32(0), "Invalid github ID");

        // Check if identity already has a canonical wallet
        if (identities[githubId].isActive) {
            // Allow re-declaration if within deadline
            _removeFromWalletMapping(githubId, identities[githubId].canonicalWallet);
        }

        // Update identity
        identities[githubId] = ContributorIdentity({
            githubId: githubId,
            canonicalWallet: wallet,
            declarationTimestamp: block.timestamp,
            isActive: true
        });

        // Update mappings
        walletToGithubIds[wallet].add(githubId);
        allGithubIds.add(githubId);
        allWallets.add(wallet);

        emit CanonicalWalletDeclared(githubId, wallet, block.timestamp);
    }

    function resolveCluster(bytes32 primaryGithubId, bytes32[] calldata secondaryIds) external onlyOwner onlyAfterAudit {
        require(identities[primaryGithubId].isActive, "Primary identity not declared");
        address canonicalWallet = identities[primaryGithubId].canonicalWallet;

        for (uint256 i = 0; i < secondaryIds.length; i++) {
            bytes32 secondaryId = secondaryIds[i];
            require(flaggedIdentities[secondaryId], "Secondary identity not flagged");

            address oldWallet = identities[secondaryId].canonicalWallet;
            if (oldWallet != address(0)) {
                _removeFromWalletMapping(secondaryId, oldWallet);
            }

            // Assign to primary wallet
            identities[secondaryId] = ContributorIdentity({
                githubId: secondaryId,
                canonicalWallet: canonicalWallet,
                declarationTimestamp: block.timestamp,
                isActive: true
            });

            walletToGithubIds[canonicalWallet].add(secondaryId);
            flaggedIdentities[secondaryId] = false;

            emit ClusterResolved(secondaryId, oldWallet, canonicalWallet);
        }
    }

    // --- View Functions ---
    function getCanonicalWallet(bytes32 githubId) external view returns (address) {
        require(identities[githubId].isActive, "Identity not declared");
        return identities[githubId].canonicalWallet;
    }

    function getAssociatedGithubIds(address wallet) external view returns (bytes32[] memory) {
        uint256 length = walletToGithubIds[wallet].length();
        bytes32[] memory ids = new bytes32[](length);
        for (uint256 i = 0; i < length; i++) {
            ids[i] = walletToGithubIds[wallet].at(i);
        }
        return ids;
    }

    function isFlagged(bytes32 githubId) external view returns (bool) {
        return flaggedIdentities[githubId];
    }

    function getAuditClusterCount() external view returns (uint256) {
        return auditClusters.length;
    }

    function getAuditCluster(uint256 index) external view returns (WalletCluster memory) {
        require(index < auditClusters.length, "Index out of bounds");
        return auditClusters[index];
    }

    function getDeclarationDeadline() external view returns (uint256) {
        return declarationDeadline;
    }

    function getIdentityCount() external view returns (uint256) {
        return allGithubIds.length();
    }

    function getWalletCount() external view returns (uint256) {
        return allWallets.length();
    }

    // --- Internal ---
    function _removeFromWalletMapping(bytes32 githubId, address wallet) internal {
        walletToGithubIds[wallet].remove(githubId);
        if (walletToGithubIds[wallet].length() == 0) {
            allWallets.remove(wallet);
        }
    }
}