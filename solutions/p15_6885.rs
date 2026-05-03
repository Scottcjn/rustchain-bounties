// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

contract CanonicalWalletRegistry is Ownable {
    using ECDSA for bytes32;

    struct Declaration {
        address wallet;
        uint256 timestamp;
        bool finalized;
    }

    struct Contributor {
        bytes32 githubIdHash;
        address canonicalWallet;
        uint256 declarationDeadline;
        bool hasDeclared;
    }

    mapping(bytes32 => Contributor) public contributors;
    mapping(address => bytes32) public walletToContributor;
    mapping(bytes32 => Declaration) public declarations;

    uint256 public constant DECLARATION_PERIOD = 14 days;
    uint256 public constant AUDIT_TIMESTAMP = 1774732800; // 2026-04-27 00:00:00 UTC
    uint256 public constant DEADLINE_TIMESTAMP = 1775347200; // 2026-05-11 00:00:00 UTC

    event WalletDeclared(bytes32 indexed githubIdHash, address indexed wallet, uint256 timestamp);
    event WalletFinalized(bytes32 indexed githubIdHash, address indexed wallet);
    event WalletDisputed(bytes32 indexed githubIdHash, address indexed disputedWallet);

    constructor() Ownable(msg.sender) {}

    function declareWallet(
        bytes32 _githubIdHash,
        address _wallet,
        bytes calldata _signature
    ) external {
        require(block.timestamp <= DEADLINE_TIMESTAMP, "Declaration period ended");
        require(_wallet != address(0), "Invalid wallet address");
        require(contributors[_githubIdHash].canonicalWallet == address(0), "Already declared");

        bytes32 messageHash = keccak256(abi.encodePacked(_githubIdHash, _wallet, block.timestamp));
        bytes32 ethSignedMessageHash = messageHash.toEthSignedMessageHash();
        address signer = ethSignedMessageHash.recover(_signature);
        require(signer == _wallet, "Invalid signature");

        contributors[_githubIdHash] = Contributor({
            githubIdHash: _githubIdHash,
            canonicalWallet: _wallet,
            declarationDeadline: block.timestamp + DECLARATION_PERIOD,
            hasDeclared: true
        });

        walletToContributor[_wallet] = _githubIdHash;

        declarations[_githubIdHash] = Declaration({
            wallet: _wallet,
            timestamp: block.timestamp,
            finalized: false
        });

        emit WalletDeclared(_githubIdHash, _wallet, block.timestamp);
    }

    function finalizeDeclaration(bytes32 _githubIdHash) external {
        Declaration storage declaration = declarations[_githubIdHash];
        require(declaration.wallet != address(0), "No declaration found");
        require(!declaration.finalized, "Already finalized");
        require(block.timestamp >= declaration.timestamp + DECLARATION_PERIOD, "Declaration period not elapsed");

        declaration.finalized = true;
        emit WalletFinalized(_githubIdHash, declaration.wallet);
    }

    function disputeWallet(bytes32 _githubIdHash, address _disputedWallet) external onlyOwner {
        Declaration storage declaration = declarations[_githubIdHash];
        require(declaration.wallet != address(0), "No declaration found");
        require(!declaration.finalized, "Already finalized");

        bytes32 disputedContributor = walletToContributor[_disputedWallet];
        require(disputedContributor != bytes32(0), "No contributor for disputed wallet");
        require(disputedContributor != _githubIdHash, "Cannot dispute own wallet");

        declaration.finalized = true;
        emit WalletDisputed(_githubIdHash, _disputedWallet);
    }

    function getCanonicalWallet(bytes32 _githubIdHash) external view returns (address) {
        Contributor memory contributor = contributors[_githubIdHash];
        if (contributor.hasDeclared && block.timestamp >= contributor.declarationDeadline) {
            return contributor.canonicalWallet;
        }
        return address(0);
    }

    function isWalletFinalized(bytes32 _githubIdHash) external view returns (bool) {
        return declarations[_githubIdHash].finalized;
    }

    function getDeclarationTimestamp(bytes32 _githubIdHash) external view returns (uint256) {
        return declarations[_githubIdHash].timestamp;
    }
}