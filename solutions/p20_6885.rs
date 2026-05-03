// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";

contract CanonicalWalletRegistry is Ownable {
    using EnumerableSet for EnumerableSet.AddressSet;

    struct Contributor {
        string githubId;
        address wallet;
        uint256 declarationTimestamp;
        bool isCanonical;
    }

    mapping(string => Contributor) public contributors;
    mapping(address => EnumerableSet.AddressSet) private walletToGithubIds;
    mapping(string => EnumerableSet.AddressSet) private githubToWallets;

    event CanonicalWalletDeclared(string indexed githubId, address indexed wallet, uint256 timestamp);
    event CanonicalWalletUpdated(string indexed githubId, address indexed oldWallet, address indexed newWallet, uint256 timestamp);
    event ConflictResolved(string indexed githubId, address indexed canonicalWallet, uint256 timestamp);

    uint256 public constant DECLARATION_DEADLINE = 1715385600; // 2026-05-11 00:00:00 UTC
    uint256 public constant AUDIT_TIMESTAMP = 1714176000; // 2026-04-27 00:00:00 UTC

    constructor() Ownable(msg.sender) {}

    function declareCanonicalWallet(string calldata githubId, address wallet) external {
        require(block.timestamp <= DECLARATION_DEADLINE, "Declaration period ended");
        require(wallet != address(0), "Invalid wallet address");

        Contributor storage contributor = contributors[githubId];
        require(!contributor.isCanonical, "Canonical wallet already declared");

        if (contributor.wallet != address(0)) {
            address oldWallet = contributor.wallet;
            githubToWallets[githubId].remove(oldWallet);
            walletToGithubIds[oldWallet].remove(address(uint160(uint256(keccak256(abi.encodePacked(githubId))))));
        }

        contributor.githubId = githubId;
        contributor.wallet = wallet;
        contributor.declarationTimestamp = block.timestamp;
        contributor.isCanonical = true;

        githubToWallets[githubId].add(wallet);
        walletToGithubIds[wallet].add(address(uint160(uint256(keccak256(abi.encodePacked(githubId))))));

        emit CanonicalWalletDeclared(githubId, wallet, block.timestamp);
    }

    function updateCanonicalWallet(string calldata githubId, address newWallet) external {
        Contributor storage contributor = contributors[githubId];
        require(contributor.isCanonical, "No canonical wallet declared");
        require(block.timestamp <= DECLARATION_DEADLINE, "Declaration period ended");
        require(newWallet != address(0), "Invalid wallet address");
        require(newWallet != contributor.wallet, "Same wallet");

        address oldWallet = contributor.wallet;
        contributor.wallet = newWallet;
        contributor.declarationTimestamp = block.timestamp;

        githubToWallets[githubId].remove(oldWallet);
        githubToWallets[githubId].add(newWallet);
        walletToGithubIds[oldWallet].remove(address(uint160(uint256(keccak256(abi.encodePacked(githubId))))));
        walletToGithubIds[newWallet].add(address(uint160(uint256(keccak256(abi.encodePacked(githubId))))));

        emit CanonicalWalletUpdated(githubId, oldWallet, newWallet, block.timestamp);
    }

    function resolveConflict(string calldata githubId, address canonicalWallet) external onlyOwner {
        require(block.timestamp > DECLARATION_DEADLINE, "Declaration period still active");
        Contributor storage contributor = contributors[githubId];
        require(contributor.isCanonical, "No canonical wallet declared");

        address oldWallet = contributor.wallet;
        contributor.wallet = canonicalWallet;
        contributor.declarationTimestamp = block.timestamp;

        githubToWallets[githubId].remove(oldWallet);
        githubToWallets[githubId].add(canonicalWallet);
        walletToGithubIds[oldWallet].remove(address(uint160(uint256(keccak256(abi.encodePacked(githubId))))));
        walletToGithubIds[canonicalWallet].add(address(uint160(uint256(keccak256(abi.encodePacked(githubId))))));

        emit ConflictResolved(githubId, canonicalWallet, block.timestamp);
    }

    function getCanonicalWallet(string calldata githubId) external view returns (address) {
        Contributor memory contributor = contributors[githubId];
        require(contributor.isCanonical, "No canonical wallet declared");
        return contributor.wallet;
    }

    function getGithubIdsForWallet(address wallet) external view returns (string[] memory) {
        uint256 length = walletToGithubIds[wallet].length();
        string[] memory ids = new string[](length);
        for (uint256 i = 0; i < length; i++) {
            ids[i] = string(abi.encodePacked(walletToGithubIds[wallet].at(i)));
        }
        return ids;
    }

    function getWalletsForGithubId(string calldata githubId) external view returns (address[] memory) {
        uint256 length = githubToWallets[githubId].length();
        address[] memory wallets = new address[](length);
        for (uint256 i = 0; i < length; i++) {
            wallets[i] = githubToWallets[githubId].at(i);
        }
        return wallets;
    }

    function isDeclarationPeriodActive() external view returns (bool) {
        return block.timestamp <= DECLARATION_DEADLINE;
    }
}