// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract CanonicalWalletRegistry is Ownable {
    using Counters for Counters.Counter;

    // --- Structs ---
    struct Contributor {
        string githubIdentity;  // e.g., "username/repo"
        address wallet;
        uint256 declaredAt;
        bool isCanonical;
    }

    // --- State ---
    mapping(bytes32 => Contributor) public contributors;  // keccak256(githubIdentity)
    mapping(address => bytes32[]) public walletToIdentities;
    mapping(address => bool) public canonicalWallets;
    
    Counters.Counter private _declarationCount;
    uint256 public constant DECLARATION_DEADLINE = 2026_05_11;
    uint256 public constant AUDIT_DATE = 2026_04_27;

    // --- Events ---
    event CanonicalWalletDeclared(
        bytes32 indexed identityHash,
        string githubIdentity,
        address indexed wallet,
        uint256 timestamp
    );
    event WalletDisputed(
        address indexed wallet,
        string reason,
        uint256 timestamp
    );

    // --- Errors ---
    error DeclarationTooLate();
    error IdentityAlreadyRegistered();
    error WalletAlreadyCanonical();
    error InvalidGithubIdentity();

    // --- Constructor ---
    constructor() Ownable(msg.sender) {
        // Initialize with known clusters from forensic audit
        _registerAuditCluster("alice/contributor", "TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu");
        _registerAuditCluster("bob/developer", "TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu");
        _registerAuditCluster("charlie/coder", "TV9NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu");
        _registerAuditCluster("dave/hacker", "TV9NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu");
        _registerAuditCluster("eve/engineer", "TW0NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu");
    }

    // --- Core Functions ---
    function declareCanonicalWallet(
        string calldata githubIdentity,
        address wallet
    ) external {
        if (block.timestamp > DECLARATION_DEADLINE) revert DeclarationTooLate();
        if (bytes(githubIdentity).length == 0) revert InvalidGithubIdentity();
        
        bytes32 identityHash = keccak256(abi.encodePacked(githubIdentity));
        if (contributors[identityHash].wallet != address(0)) revert IdentityAlreadyRegistered();
        if (canonicalWallets[wallet]) revert WalletAlreadyCanonical();

        // Check if this wallet is already associated with another identity
        if (walletToIdentities[wallet].length > 0) {
            // This is a cluster case - require explicit declaration
            _handleClusterDeclaration(githubIdentity, wallet, identityHash);
        } else {
            // Fresh declaration
            contributors[identityHash] = Contributor({
                githubIdentity: githubIdentity,
                wallet: wallet,
                declaredAt: block.timestamp,
                isCanonical: true
            });
            walletToIdentities[wallet].push(identityHash);
            canonicalWallets[wallet] = true;
            _declarationCount.increment();
            
            emit CanonicalWalletDeclared(identityHash, githubIdentity, wallet, block.timestamp);
        }
    }

    function resolveDispute(bytes32 identityHash, address newWallet) external onlyOwner {
        Contributor storage contributor = contributors[identityHash];
        require(contributor.wallet != address(0), "Identity not registered");
        
        address oldWallet = contributor.wallet;
        contributor.wallet = newWallet;
        contributor.declaredAt = block.timestamp;
        
        // Remove from old wallet mapping
        _removeFromWalletMapping(oldWallet, identityHash);
        
        // Add to new wallet mapping
        walletToIdentities[newWallet].push(identityHash);
        
        emit CanonicalWalletDeclared(identityHash, contributor.githubIdentity, newWallet, block.timestamp);
    }

    function getContributorWallet(string calldata githubIdentity) external view returns (address) {
        bytes32 identityHash = keccak256(abi.encodePacked(githubIdentity));
        return contributors[identityHash].wallet;
    }

    function getIdentitiesForWallet(address wallet) external view returns (bytes32[] memory) {
        return walletToIdentities[wallet];
    }

    function isCanonicalWallet(address wallet) external view returns (bool) {
        return canonicalWallets[wallet];
    }

    function getDeclarationCount() external view returns (uint256) {
        return _declarationCount.current();
    }

    // --- Internal Helpers ---
    function _registerAuditCluster(string memory identity, string memory walletStr) internal {
        bytes32 identityHash = keccak256(abi.encodePacked(identity));
        address wallet = _parseWallet(walletStr);
        
        contributors[identityHash] = Contributor({
            githubIdentity: identity,
            wallet: wallet,
            declaredAt: AUDIT_DATE,
            isCanonical: false  // Not canonical until declared
        });
        walletToIdentities[wallet].push(identityHash);
    }

    function _handleClusterDeclaration(
        string memory githubIdentity,
        address wallet,
        bytes32 identityHash
    ) internal {
        // For clusters, we need to pick one canonical wallet per identity
        // If this wallet is already associated with another identity, we need to resolve
        
        bytes32[] storage existing = walletToIdentities[wallet];
        bool hasExistingCanonical = false;
        
        for (uint i = 0; i < existing.length; i++) {
            if (contributors[existing[i]].isCanonical) {
                hasExistingCanonical = true;
                break;
            }
        }
        
        if (hasExistingCanonical) {
            // This wallet already has a canonical identity - dispute
            emit WalletDisputed(wallet, "Wallet already canonical for another identity", block.timestamp);
            revert WalletAlreadyCanonical();
        }
        
        // Register as canonical for this identity
        contributors[identityHash] = Contributor({
            githubIdentity: githubIdentity,
            wallet: wallet,
            declaredAt: block.timestamp,
            isCanonical: true
        });
        walletToIdentities[wallet].push(identityHash);
        canonicalWallets[wallet] = true;
        _declarationCount.increment();
        
        emit CanonicalWalletDeclared(identityHash, githubIdentity, wallet, block.timestamp);
    }

    function _removeFromWalletMapping(address wallet, bytes32 identityHash) internal {
        bytes32[] storage identities = walletToIdentities[wallet];
        for (uint i = 0; i < identities.length; i++) {
            if (identities[i] == identityHash) {
                identities[i] = identities[identities.length - 1];
                identities.pop();
                break;
            }
        }
        if (identities.length == 0) {
            delete canonicalWallets[wallet];
        }
    }

    function _parseWallet(string memory walletStr) internal pure returns (address) {
        // Simple parsing for TON-style addresses (base64)
        // In production, use proper address parsing
        bytes memory addrBytes = bytes(walletStr);
        require(addrBytes.length == 34, "Invalid wallet address length");
        
        // Simplified conversion - in production use proper base64 decoding
        return address(uint160(uint256(keccak256(abi.encodePacked(walletStr)))));
    }

    // --- Fallback ---
    receive() external payable {}
}