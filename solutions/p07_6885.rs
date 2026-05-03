// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";

contract CanonicalWalletRegistry is Ownable {
    using Counters for Counters.Counter;
    using EnumerableSet for EnumerableSet.AddressSet;

    // --- Structs ---
    struct Contributor {
        string githubId;          // e.g., "octocat"
        address rtcWallet;        // canonical RTC wallet
        uint256 declaredAt;       // timestamp of declaration
        bool isActive;            // false if superseded
    }

    struct Declaration {
        string githubId;
        address wallet;
        uint256 timestamp;
        string proof;             // IPFS hash or signed message
    }

    // --- State ---
    mapping(string => Contributor) public contributors;          // githubId -> Contributor
    mapping(address => string[]) public walletToGithubIds;      // wallet -> list of githubIds
    mapping(string => Declaration[]) public declarationHistory; // githubId -> history

    EnumerableSet.AddressSet private canonicalWallets;
    EnumerableSet.AddressSet private disputedWallets;

    Counters.Counter private _declarationCounter;
    uint256 public constant DECLARATION_DEADLINE = 2026_05_11;  // Unix timestamp: 2026-05-11 00:00:00 UTC

    // --- Events ---
    event CanonicalWalletDeclared(
        string indexed githubId,
        address indexed wallet,
        uint256 timestamp,
        string proof
    );

    event WalletDisputed(
        address indexed wallet,
        string[] conflictingGithubIds,
        uint256 timestamp
    );

    event WalletCanonicalized(
        address indexed wallet,
        string indexed canonicalGithubId,
        uint256 timestamp
    );

    // --- Errors ---
    error DeadlinePassed();
    error WalletAlreadyCanonical(address wallet);
    error GithubIdAlreadyCanonical(string githubId);
    error InvalidProof();
    error WalletNotCanonical(address wallet);
    error NoDeclarationFound(string githubId);

    // --- Constructor ---
    constructor() Ownable(msg.sender) {}

    // --- Core Functions ---

    /**
     * @dev Declare a canonical RTC wallet for a GitHub identity.
     * @param githubId The GitHub username (lowercase).
     * @param wallet The RTC wallet address.
     * @param proof Signed message or IPFS hash proving ownership.
     */
    function declareCanonicalWallet(
        string calldata githubId,
        address wallet,
        string calldata proof
    ) external {
        if (block.timestamp > DECLARATION_DEADLINE) revert DeadlinePassed();

        string memory lowerGithubId = _toLower(githubId);

        // Check if this githubId already has an active canonical wallet
        if (contributors[lowerGithubId].isActive) {
            revert GithubIdAlreadyCanonical(lowerGithubId);
        }

        // Check if this wallet is already canonical for another githubId
        if (canonicalWallets.contains(wallet)) {
            revert WalletAlreadyCanonical(wallet);
        }

        // Verify proof (simplified - in production would verify EIP-712 signature)
        if (bytes(proof).length == 0) revert InvalidProof();

        // Store declaration
        contributors[lowerGithubId] = Contributor({
            githubId: lowerGithubId,
            rtcWallet: wallet,
            declaredAt: block.timestamp,
            isActive: true
        });

        walletToGithubIds[wallet].push(lowerGithubId);
        canonicalWallets.add(wallet);

        declarationHistory[lowerGithubId].push(Declaration({
            githubId: lowerGithubId,
            wallet: wallet,
            timestamp: block.timestamp,
            proof: proof
        }));

        _declarationCounter.increment();

        emit CanonicalWalletDeclared(lowerGithubId, wallet, block.timestamp, proof);
    }

    /**
     * @dev Resolve a dispute where multiple githubIds claim the same wallet.
     * @param wallet The disputed wallet address.
     * @param canonicalGithubId The githubId that should keep the wallet.
     * @param proof Proof that canonicalGithubId owns the wallet.
     */
    function resolveDispute(
        address wallet,
        string calldata canonicalGithubId,
        string calldata proof
    ) external onlyOwner {
        string memory lowerGithubId = _toLower(canonicalGithubId);

        // Verify the wallet is disputed
        if (!disputedWallets.contains(wallet)) {
            revert WalletNotCanonical(wallet);
        }

        // Verify proof
        if (bytes(proof).length == 0) revert InvalidProof();

        // Deactivate other githubIds
        string[] memory conflictingIds = walletToGithubIds[wallet];
        for (uint256 i = 0; i < conflictingIds.length; i++) {
            if (keccak256(bytes(conflictingIds[i])) != keccak256(bytes(lowerGithubId))) {
                contributors[conflictingIds[i]].isActive = false;
            }
        }

        // Set canonical
        contributors[lowerGithubId].isActive = true;
        contributors[lowerGithubId].rtcWallet = wallet;
        contributors[lowerGithubId].declaredAt = block.timestamp;

        disputedWallets.remove(wallet);
        canonicalWallets.add(wallet);

        emit WalletCanonicalized(wallet, lowerGithubId, block.timestamp);
    }

    /**
     * @dev Flag a wallet as disputed (multiple githubIds claim it).
     * @param wallet The wallet address.
     */
    function flagDispute(address wallet) external onlyOwner {
        if (walletToGithubIds[wallet].length < 2) {
            revert WalletNotCanonical(wallet);
        }

        disputedWallets.add(wallet);
        canonicalWallets.remove(wallet);

        emit WalletDisputed(wallet, walletToGithubIds[wallet], block.timestamp);
    }

    /**
     * @dev Get the canonical wallet for a githubId.
     * @param githubId The GitHub username.
     * @return wallet The canonical RTC wallet address.
     */
    function getCanonicalWallet(string calldata githubId) external view returns (address wallet) {
        string memory lowerGithubId = _toLower(githubId);
        Contributor memory contributor = contributors[lowerGithubId];
        if (!contributor.isActive) revert NoDeclarationFound(lowerGithubId);
        return contributor.rtcWallet;
    }

    /**
     * @dev Get all githubIds associated with a wallet.
     * @param wallet The wallet address.
     * @return githubIds Array of githubIds.
     */
    function getGithubIdsForWallet(address wallet) external view returns (string[] memory) {
        return walletToGithubIds[wallet];
    }

    /**
     * @dev Check if a wallet is canonical.
     * @param wallet The wallet address.
     * @return isCanonical True if wallet is canonical.
     */
    function isCanonicalWallet(address wallet) external view returns (bool) {
        return canonicalWallets.contains(wallet);
    }

    /**
     * @dev Check if a wallet is disputed.
     * @param wallet The wallet address.
     * @return isDisputed True if wallet is disputed.
     */
    function isDisputedWallet(address wallet) external view returns (bool) {
        return disputedWallets.contains(wallet);
    }

    /**
     * @dev Get total declarations made.
     * @return count Number of declarations.
     */
    function getDeclarationCount() external view returns (uint256) {
        return _declarationCounter.current();
    }

    /**
     * @dev Get declaration history for a githubId.
     * @param githubId The GitHub username.
     * @return history Array of declarations.
     */
    function getDeclarationHistory(string calldata githubId) external view returns (Declaration[] memory) {
        return declarationHistory[_toLower(githubId)];
    }

    // --- Internal Helpers ---

    /**
     * @dev Convert string to lowercase (ASCII only).
     * @param str The input string.
     * @return The lowercase string.
     */
    function _toLower(string memory str) internal pure returns (string memory) {
        bytes memory bStr = bytes(str);
        bytes memory bLower = new bytes(bStr.length);
        for (uint256 i = 0; i < bStr.length; i++) {
            if ((uint8(bStr[i]) >= 65) && (uint8(bStr[i]) <= 90)) {
                bLower[i] = bytes1(uint8(bStr[i]) + 32);
            } else {
                bLower[i] = bStr[i];
            }
        }
        return string(bLower);
    }

    // --- Fallback ---
    receive() external payable {
        revert("No ETH accepted");
    }
}