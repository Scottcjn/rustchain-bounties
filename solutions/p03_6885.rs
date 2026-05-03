// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";

/**
 * @title CanonicalWalletRegistry
 * @notice Implements the RTC wallet policy: one canonical wallet per contributor identity.
 * @dev Contributors must declare their canonical payout wallet by 2026-05-11.
 *      After the deadline, wallets are inferred per-PR basis.
 */
contract CanonicalWalletRegistry is Ownable {
    using ECDSA for bytes32;
    using MessageHashUtils for bytes32;

    // --- Structs ---
    struct Declaration {
        address wallet;
        uint256 timestamp;
        bool isActive;
    }

    // --- State ---
    // Mapping from GitHub identity (keccak256 of username) to canonical wallet
    mapping(bytes32 => Declaration) public canonicalWallets;
    
    // Mapping from wallet to the identity that claimed it
    mapping(address => bytes32) public walletToIdentity;

    // Mapping from PR hash to wallet (inferred after deadline)
    mapping(bytes32 => address) public perPRWallets;

    // Deadline timestamp: 2026-05-11 00:00:00 UTC
    uint256 public constant DECLARATION_DEADLINE = 1778025600;

    // Audit timestamp: 2026-04-27 00:00:00 UTC
    uint256 public constant AUDIT_TIMESTAMP = 1777420800;

    // Events
    event CanonicalWalletDeclared(
        bytes32 indexed identityHash,
        address indexed wallet,
        uint256 timestamp
    );

    event CanonicalWalletUpdated(
        bytes32 indexed identityHash,
        address indexed oldWallet,
        address indexed newWallet,
        uint256 timestamp
    );

    event PRWalletInferred(
        bytes32 indexed prHash,
        address indexed wallet,
        bytes32 indexed identityHash
    );

    event WalletConflictResolved(
        bytes32 indexed identityHash,
        address indexed retainedWallet,
        address indexed removedWallet
    );

    // --- Errors ---
    error DeadlinePassed();
    error WalletAlreadyClaimed(address wallet);
    error IdentityAlreadyDeclared(bytes32 identityHash);
    error NoCanonicalWallet(bytes32 identityHash);
    error InvalidSignature();
    error NotAuthorized();

    // --- Constructor ---
    constructor() Ownable(msg.sender) {}

    // --- Modifiers ---
    modifier beforeDeadline() {
        if (block.timestamp >= DECLARATION_DEADLINE) revert DeadlinePassed();
        _;
    }

    // --- Core Functions ---

    /**
     * @notice Declare a canonical wallet for a GitHub identity.
     * @param identityHash keccak256 hash of the GitHub username
     * @param wallet The RTC wallet address
     * @param signature EIP-712 signature proving ownership of the wallet
     */
    function declareCanonicalWallet(
        bytes32 identityHash,
        address wallet,
        bytes calldata signature
    ) external beforeDeadline {
        // Verify wallet ownership via signature
        bytes32 messageHash = keccak256(
            abi.encodePacked(
                "\x19Ethereum Signed Message:\n32",
                keccak256(abi.encodePacked(identityHash, wallet, block.timestamp))
            )
        );
        address signer = messageHash.recover(signature);
        if (signer != wallet) revert InvalidSignature();

        // Check wallet not already claimed
        if (walletToIdentity[wallet] != bytes32(0)) {
            revert WalletAlreadyClaimed(wallet);
        }

        // Check identity not already declared
        if (canonicalWallets[identityHash].isActive) {
            revert IdentityAlreadyDeclared(identityHash);
        }

        // Store declaration
        canonicalWallets[identityHash] = Declaration({
            wallet: wallet,
            timestamp: block.timestamp,
            isActive: true
        });
        walletToIdentity[wallet] = identityHash;

        emit CanonicalWalletDeclared(identityHash, wallet, block.timestamp);
    }

    /**
     * @notice Update canonical wallet (only before deadline).
     * @param identityHash keccak256 hash of the GitHub username
     * @param newWallet New RTC wallet address
     * @param signature EIP-712 signature proving ownership of the new wallet
     */
    function updateCanonicalWallet(
        bytes32 identityHash,
        address newWallet,
        bytes calldata signature
    ) external beforeDeadline {
        Declaration storage current = canonicalWallets[identityHash];
        if (!current.isActive) revert NoCanonicalWallet(identityHash);

        // Verify new wallet ownership
        bytes32 messageHash = keccak256(
            abi.encodePacked(
                "\x19Ethereum Signed Message:\n32",
                keccak256(abi.encodePacked(identityHash, newWallet, block.timestamp))
            )
        );
        address signer = messageHash.recover(signature);
        if (signer != newWallet) revert InvalidSignature();

        // Check new wallet not already claimed by another identity
        bytes32 existingIdentity = walletToIdentity[newWallet];
        if (existingIdentity != bytes32(0) && existingIdentity != identityHash) {
            revert WalletAlreadyClaimed(newWallet);
        }

        address oldWallet = current.wallet;

        // Update mappings
        delete walletToIdentity[oldWallet];
        current.wallet = newWallet;
        current.timestamp = block.timestamp;
        walletToIdentity[newWallet] = identityHash;

        emit CanonicalWalletUpdated(identityHash, oldWallet, newWallet, block.timestamp);
    }

    /**
     * @notice Resolve wallet conflict for a cluster of identities sharing a wallet.
     * @dev Only callable by owner after audit.
     * @param identityHashes Array of identity hashes in the cluster
     * @param retainedWallet The wallet to keep as canonical
     */
    function resolveWalletConflict(
        bytes32[] calldata identityHashes,
        address retainedWallet
    ) external onlyOwner {
        require(block.timestamp >= AUDIT_TIMESTAMP, "Audit not yet performed");

        // Verify retained wallet is claimed by one of the identities
        bytes32 retainedIdentity = walletToIdentity[retainedWallet];
        bool found = false;
        for (uint256 i = 0; i < identityHashes.length; i++) {
            if (identityHashes[i] == retainedIdentity) {
                found = true;
                break;
            }
        }
        require(found, "Retained wallet not in cluster");

        // Remove other wallets from the cluster
        for (uint256 i = 0; i < identityHashes.length; i++) {
            bytes32 idHash = identityHashes[i];
            if (idHash == retainedIdentity) continue;

            Declaration storage decl = canonicalWallets[idHash];
            if (decl.isActive) {
                address walletToRemove = decl.wallet;
                delete walletToIdentity[walletToRemove];
                decl.isActive = false;
                emit WalletConflictResolved(idHash, retainedWallet, walletToRemove);
            }
        }
    }

    /**
     * @notice Infer wallet for a PR after the deadline.
     * @param prHash keccak256 hash of the PR identifier
     * @param identityHash keccak256 hash of the contributor's GitHub username
     */
    function inferPRWallet(
        bytes32 prHash,
        bytes32 identityHash
    ) external {
        require(block.timestamp >= DECLARATION_DEADLINE, "Deadline not yet passed");

        address wallet;
        Declaration storage decl = canonicalWallets[identityHash];
        if (decl.isActive) {
            wallet = decl.wallet;
        } else {
            // Fallback: use the wallet from the PR submission (simplified)
            // In production, this would be extracted from the PR metadata
            wallet = address(0); // Placeholder
        }

        perPRWallets[prHash] = wallet;
        emit PRWalletInferred(prHash, wallet, identityHash);
    }

    /**
     * @notice Get canonical wallet for an identity.
     * @param identityHash keccak256 hash of the GitHub username
     * @return wallet The canonical wallet address (zero if not declared)
     */
    function getCanonicalWallet(bytes32 identityHash) external view returns (address) {
        Declaration storage decl = canonicalWallets[identityHash];
        if (decl.isActive) {
            return decl.wallet;
        }
        return address(0);
    }

    /**
     * @notice Get the identity that claimed a wallet.
     * @param wallet The RTC wallet address
     * @return identityHash keccak256 hash of the GitHub username (zero if unclaimed)
     */
    function getIdentityByWallet(address wallet) external view returns (bytes32) {
        return walletToIdentity[wallet];
    }

    /**
     * @notice Check if a wallet is canonical for any identity.
     * @param wallet The RTC wallet address
     * @return isCanonical True if the wallet is claimed as canonical
     */
    function isCanonicalWallet(address wallet) external view returns (bool) {
        return walletToIdentity[wallet] != bytes32(0);
    }

    /**
     * @notice Get the inferred wallet for a PR.
     * @param prHash keccak256 hash of the PR identifier
     * @return wallet The inferred wallet address
     */
    function getPRWallet(bytes32 prHash) external view returns (address) {
        return perPRWallets[prHash];
    }

    /**
     * @notice Check if the declaration deadline has passed.
     * @return passed True if deadline has passed
     */
    function isDeadlinePassed() external view returns (bool) {
        return block.timestamp >= DECLARATION_DEADLINE;
    }

    /**
     * @notice Get the current timestamp for testing purposes.
     * @return timestamp Current block timestamp
     */
    function getCurrentTimestamp() external view returns (uint256) {
        return block.timestamp;
    }
}