// SPDX-License-Identifier: MIT
// Compatible with OpenZeppelin Contracts ^5.0.0
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title wRTC - Wrapped RTC on Base
 * @dev ERC-20 token for cross-chain airdrop (RIP-305)
 * 
 * Track B: Base ERC-20 Token (75 RTC Bounty)
 * 
 * Features:
 * - 6 decimal precision (matches RTC)
 * - Mint/burn functionality for bridge integration
 * - Ownable for bridge authority
 * - OpenZeppelin ERC-20 standard
 */
contract wRTC is ERC20, ERC20Burnable, Ownable {
    // 6 decimals to match RTC main chain
    uint8 private constant DECIMALS = 6;
    
    // Mint event for bridge tracking
    event TokensMinted(address indexed to, uint256 amount);
    
    // Burn event for bridge tracking
    event TokensBurned(address indexed from, uint256 amount);

    /**
     * @dev Constructor - no initial supply
     * Tokens will be minted as needed for airdrop and bridge operations
     */
    constructor()
        ERC20("Wrapped RTC", "wRTC")
        Ownable(msg.sender)
    {}

    /**
     * @dev Returns the number of decimals used to get its user representation.
     * @return uint8 number of decimals (6)
     */
    function decimals() public pure override returns (uint8) {
        return DECIMALS;
    }

    /**
     * @dev Mint tokens - only owner (bridge contract) can call
     * @param to Address to mint tokens to
     * @param amount Amount of tokens to mint
     */
    function mint(address to, uint256 amount) public onlyOwner {
        _mint(to, amount);
        emit TokensMinted(to, amount);
    }

    /**
     * @dev Burn tokens - any holder can burn their own tokens
     * @param amount Amount of tokens to burn
     */
    function burn(uint256 amount) public override {
        super.burn(amount);
        emit TokensBurned(msg.sender, amount);
    }

    /**
     * @dev Burn tokens from another address - allowance required
     * @param account Address to burn tokens from
     * @param amount Amount of tokens to burn
     */
    function burnFrom(address account, uint256 amount) public override {
        super.burnFrom(account, amount);
        emit TokensBurned(account, amount);
    }

    /**
     * @dev Transfer ownership to bridge contract after deployment
     * @param newOwner Address of the bridge contract
     */
    function transferBridgeOwnership(address newOwner) public onlyOwner {
        transferOwnership(newOwner);
    }
}
