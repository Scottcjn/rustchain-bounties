// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract CanonicalWalletRegistry is Ownable, ReentrancyGuard {
    // --- Structs ---
    struct ContributorIdentity {
        string githubUsername;
        address canonicalWallet;
        uint256 declarationTimestamp;
        bool isActive;
    }

    struct WalletCluster {
        address walletAddress;
        bytes32[] identityHashes;
        uint256 clusterSize;
    }

    // --- State ---
    mapping(bytes32 => ContributorIdentity) public identities;
    mapping(address => bytes32[]) public walletToIdentities;
    mapping(address => bool) public canonicalWallets;
    mapping(address => uint256) public walletDeclarationCount;

    bytes32[] private allIdentityHashes;
    uint256 public constant DECLARATION_DEADLINE = 1715385600; // 2026-05-11 00:00:00 UTC
    uint256 public constant AUDIT_TIMESTAMP = 1714176000; // 2026-04-27 00:00:00 UTC

    // --- Events ---
    event CanonicalWalletDeclared(
        bytes32 indexed identityHash,
        string githubUsername,
        address indexed wallet,
        uint256 timestamp
    );
    event WalletClustered(
        address indexed wallet,
        uint256 clusterSize,
        bytes32[] identityHashes
    );
    event PolicyEnforced(
        bytes32 indexed identityHash,
        address indexed oldWallet,
        address indexed newCanonicalWallet
    );

    // --- Modifiers ---
    modifier beforeDeadline() {
        require(block.timestamp <= DECLARATION_DEADLINE, "Declaration period ended");
        _;
    }

    modifier onlyActiveIdentity(bytes32 identityHash) {
        require(identities[identityHash].isActive, "Identity not active");
        _;
    }

    // --- Core Functions ---

    /**
     * @dev Declare a canonical RTC wallet for a contributor identity
     * @param githubUsername Contributor's GitHub username
     * @param wallet The canonical RTC wallet address
     */
    function declareCanonicalWallet(
        string calldata githubUsername,
        address wallet
    ) external beforeDeadline nonReentrant {
        require(wallet != address(0), "Invalid wallet address");
        require(bytes(githubUsername).length > 0, "Username required");

        bytes32 identityHash = keccak256(abi.encodePacked(githubUsername));
        require(!identities[identityHash].isActive, "Identity already declared");

        // Check if this wallet is already canonical for another identity
        if (canonicalWallets[wallet]) {
            require(
                walletDeclarationCount[wallet] < 2,
                "Wallet already canonical for 2+ identities"
            );
        }

        identities[identityHash] = ContributorIdentity({
            githubUsername: githubUsername,
            canonicalWallet: wallet,
            declarationTimestamp: block.timestamp,
            isActive: true
        });

        walletToIdentities[wallet].push(identityHash);
        allIdentityHashes.push(identityHash);
        canonicalWallets[wallet] = true;
        walletDeclarationCount[wallet]++;

        emit CanonicalWalletDeclared(identityHash, githubUsername, wallet, block.timestamp);
    }

    /**
     * @dev Resolve conflicts where multiple identities share a wallet
     * @param identityHashes Array of identity hashes to resolve
     * @param canonicalWallet The single canonical wallet for all identities
     */
    function resolveWalletConflict(
        bytes32[] calldata identityHashes,
        address canonicalWallet
    ) external onlyOwner nonReentrant {
        require(identityHashes.length >= 2, "Need at least 2 identities");
        require(canonicalWallet != address(0), "Invalid wallet");

        for (uint256 i = 0; i < identityHashes.length; i++) {
            require(identities[identityHashes[i]].isActive, "Identity not active");
            identities[identityHashes[i]].canonicalWallet = canonicalWallet;
            emit PolicyEnforced(identityHashes[i], address(0), canonicalWallet);
        }

        // Update wallet mappings
        walletToIdentities[canonicalWallet] = identityHashes;
        canonicalWallets[canonicalWallet] = true;
        walletDeclarationCount[canonicalWallet] = identityHashes.length;
    }

    /**
     * @dev Get all identities associated with a wallet
     * @param wallet The wallet address
     * @return Array of identity hashes
     */
    function getIdentitiesForWallet(
        address wallet
    ) external view returns (bytes32[] memory) {
        return walletToIdentities[wallet];
    }

    /**
     * @dev Get cluster information for a wallet
     * @param wallet The wallet address
     * @return WalletCluster struct
     */
    function getWalletCluster(address wallet) external view returns (WalletCluster memory) {
        bytes32[] memory identities_ = walletToIdentities[wallet];
        return WalletCluster({
            walletAddress: wallet,
            identityHashes: identities_,
            clusterSize: identities_.length
        });
    }

    /**
     * @dev Check if a wallet is canonical
     * @param wallet The wallet address
     * @return bool
     */
    function isCanonicalWallet(address wallet) external view returns (bool) {
        return canonicalWallets[wallet];
    }

    /**
     * @dev Get all declared identities
     * @return Array of identity hashes
     */
    function getAllIdentities() external view returns (bytes32[] memory) {
        return allIdentityHashes;
    }

    /**
     * @dev Get identity details
     * @param identityHash The identity hash
     * @return ContributorIdentity struct
     */
    function getIdentity(bytes32 identityHash) external view returns (ContributorIdentity memory) {
        return identities[identityHash];
    }

    /**
     * @dev Check if declaration deadline has passed
     * @return bool
     */
    function isDeadlinePassed() external view returns (bool) {
        return block.timestamp > DECLARATION_DEADLINE;
    }

    /**
     * @dev Get the inferred per-PR wallet for an identity after deadline
     * @param identityHash The identity hash
     * @return address The inferred wallet
     */
    function getInferredWallet(bytes32 identityHash) external view returns (address) {
        if (block.timestamp <= DECLARATION_DEADLINE) {
            return identities[identityHash].canonicalWallet;
        }
        // After deadline, return the first declared wallet for this identity
        return identities[identityHash].canonicalWallet;
    }
}