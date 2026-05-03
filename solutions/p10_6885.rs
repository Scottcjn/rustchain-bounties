// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";

contract CanonicalWalletRegistry is Ownable {
    using ECDSA for bytes32;
    using MessageHashUtils for bytes32;

    struct ContributorIdentity {
        string githubUsername;
        address canonicalWallet;
        uint256 declarationTimestamp;
        bool isActive;
    }

    struct WalletCluster {
        address wallet;
        string[] githubIdentities;
        uint256 lastUpdated;
    }

    // Mapping from GitHub username (hashed) to contributor identity
    mapping(bytes32 => ContributorIdentity) public identities;
    
    // Mapping from wallet address to cluster info
    mapping(address => WalletCluster) public walletClusters;
    
    // Set of all registered GitHub usernames (hashed)
    bytes32[] private registeredIdentities;
    
    // Deadline for declaration (2026-05-11 23:59:59 UTC)
    uint256 public constant DECLARATION_DEADLINE = 1778543999;
    
    // Audit timestamp (2026-04-27 00:00:00 UTC)
    uint256 public constant AUDIT_TIMESTAMP = 1778198400;
    
    // Events
    event CanonicalWalletDeclared(bytes32 indexed githubHash, string githubUsername, address wallet);
    event WalletClusterUpdated(address indexed wallet, string[] githubIdentities);
    event IdentityDeactivated(bytes32 indexed githubHash);
    event InferenceTriggered(bytes32 indexed githubHash, address inferredWallet);

    // Errors
    error DeadlinePassed();
    error IdentityAlreadyRegistered(bytes32 githubHash);
    error WalletAlreadyInCluster(address wallet, string githubUsername);
    error InvalidSignature();
    error NoIdentityFound(bytes32 githubHash);
    error ClusterConflict(address wallet1, address wallet2);

    constructor() Ownable(msg.sender) {}

    /**
     * @dev Declare canonical wallet for a GitHub identity
     * @param githubUsername The GitHub username
     * @param wallet The canonical RTC wallet address
     * @param signature EIP-712 signature proving ownership of the wallet
     */
    function declareCanonicalWallet(
        string calldata githubUsername,
        address wallet,
        bytes calldata signature
    ) external {
        if (block.timestamp > DECLARATION_DEADLINE) revert DeadlinePassed();
        
        bytes32 githubHash = keccak256(abi.encodePacked(githubUsername));
        
        // Verify wallet ownership via signature
        bytes32 messageHash = keccak256(abi.encodePacked(
            "\x19Ethereum Signed Message:\n32",
            keccak256(abi.encodePacked(githubUsername, wallet, address(this)))
        ));
        
        address signer = messageHash.recover(signature);
        if (signer != wallet) revert InvalidSignature();
        
        // Check if identity already exists
        if (identities[githubHash].isActive) {
            // Allow re-declaration only if wallet matches
            if (identities[githubHash].canonicalWallet != wallet) {
                revert IdentityAlreadyRegistered(githubHash);
            }
            return;
        }
        
        // Check for wallet cluster conflicts
        WalletCluster storage cluster = walletClusters[wallet];
        for (uint i = 0; i < cluster.githubIdentities.length; i++) {
            if (keccak256(abi.encodePacked(cluster.githubIdentities[i])) == githubHash) {
                revert WalletAlreadyInCluster(wallet, githubUsername);
            }
        }
        
        // Register identity
        identities[githubHash] = ContributorIdentity({
            githubUsername: githubUsername,
            canonicalWallet: wallet,
            declarationTimestamp: block.timestamp,
            isActive: true
        });
        
        // Update wallet cluster
        cluster.githubIdentities.push(githubUsername);
        cluster.lastUpdated = block.timestamp;
        cluster.wallet = wallet;
        
        registeredIdentities.push(githubHash);
        
        emit CanonicalWalletDeclared(githubHash, githubUsername, wallet);
        emit WalletClusterUpdated(wallet, cluster.githubIdentities);
    }

    /**
     * @dev Get canonical wallet for a GitHub identity
     * @param githubUsername The GitHub username
     * @return wallet The canonical wallet address
     */
    function getCanonicalWallet(string calldata githubUsername) external view returns (address) {
        bytes32 githubHash = keccak256(abi.encodePacked(githubUsername));
        ContributorIdentity storage identity = identities[githubHash];
        
        if (!identity.isActive) revert NoIdentityFound(githubHash);
        
        return identity.canonicalWallet;
    }

    /**
     * @dev Get all GitHub identities associated with a wallet
     * @param wallet The wallet address
     * @return githubIdentities Array of GitHub usernames
     */
    function getWalletCluster(address wallet) external view returns (string[] memory) {
        return walletClusters[wallet].githubIdentities;
    }

    /**
     * @dev Infer canonical wallet per-PR basis (fallback after deadline)
     * @param githubUsername The GitHub username
     * @param prWallet The wallet used in a specific PR
     * @return inferredWallet The inferred canonical wallet
     */
    function inferPerPRWallet(
        string calldata githubUsername,
        address prWallet
    ) external view returns (address) {
        bytes32 githubHash = keccak256(abi.encodePacked(githubUsername));
        ContributorIdentity storage identity = identities[githubHash];
        
        // If identity exists and is active, return declared wallet
        if (identity.isActive) {
            return identity.canonicalWallet;
        }
        
        // After deadline, infer per-PR
        if (block.timestamp > DECLARATION_DEADLINE) {
            return prWallet;
        }
        
        revert NoIdentityFound(githubHash);
    }

    /**
     * @dev Deactivate an identity (for cleanup)
     * @param githubUsername The GitHub username
     */
    function deactivateIdentity(string calldata githubUsername) external onlyOwner {
        bytes32 githubHash = keccak256(abi.encodePacked(githubUsername));
        ContributorIdentity storage identity = identities[githubHash];
        
        if (!identity.isActive) revert NoIdentityFound(githubHash);
        
        identity.isActive = false;
        
        // Remove from wallet cluster
        WalletCluster storage cluster = walletClusters[identity.canonicalWallet];
        string[] memory remaining = new string[](cluster.githubIdentities.length - 1);
        uint256 index = 0;
        
        for (uint i = 0; i < cluster.githubIdentities.length; i++) {
            if (keccak256(abi.encodePacked(cluster.githubIdentities[i])) != githubHash) {
                remaining[index] = cluster.githubIdentities[i];
                index++;
            }
        }
        
        cluster.githubIdentities = remaining;
        cluster.lastUpdated = block.timestamp;
        
        emit IdentityDeactivated(githubHash);
        emit WalletClusterUpdated(identity.canonicalWallet, cluster.githubIdentities);
    }

    /**
     * @dev Get total number of registered identities
     */
    function getIdentityCount() external view returns (uint256) {
        return registeredIdentities.length;
    }

    /**
     * @dev Check if an identity has declared by deadline
     */
    function hasDeclaredByDeadline(string calldata githubUsername) external view returns (bool) {
        bytes32 githubHash = keccak256(abi.encodePacked(githubUsername));
        ContributorIdentity storage identity = identities[githubHash];
        
        return identity.isActive && identity.declarationTimestamp <= DECLARATION_DEADLINE;
    }

    /**
     * @dev Batch declare canonical wallets (for migration)
     */
    function batchDeclare(
        string[] calldata githubUsernames,
        address[] calldata wallets,
        bytes[] calldata signatures
    ) external {
        require(
            githubUsernames.length == wallets.length && 
            wallets.length == signatures.length,
            "Array length mismatch"
        );
        
        for (uint i = 0; i < githubUsernames.length; i++) {
            this.declareCanonicalWallet(githubUsernames[i], wallets[i], signatures[i]);
        }
    }
}