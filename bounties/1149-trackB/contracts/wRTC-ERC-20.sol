// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title wRTC (Wrapped RTC)
 * @dev Implementation of the wRTC Token on Base chain.
 * Matches RTC main chain precision (6 decimals).
 * Includes burnable and ownable functionality.
 */
contract wRTC is ERC20, ERC20Burnable, Ownable {
    
    event TokensMinted(address indexed to, uint256 amount);

    /**
     * @dev Sets up the token with name "Wrapped RTC" and symbol "wRTC".
     * Ownership is initially set to the deployer.
     */
    constructor() ERC20("Wrapped RTC", "wRTC") Ownable(msg.sender) {
    }

    /**
     * @dev Overrides decimals to match the RTC main chain (6 decimals).
     */
    function decimals() public view virtual override returns (uint8) {
        return 6;
    }

    /**
     * @dev Function to mint new tokens. Only the owner (bridge) can call this.
     * @param to The address that will receive the minted tokens.
     * @param amount The amount of tokens to mint.
     */
    function mint(address to, uint256 amount) public onlyOwner {
        _mint(to, amount);
        emit TokensMinted(to, amount);
    }

    /**
     * @dev Helper to transfer ownership to the bridge contract after deployment.
     * @param newBridge The address of the bridge contract.
     */
    function transferBridgeOwnership(address newBridge) public onlyOwner {
        require(newBridge != address(0), "New bridge cannot be zero address");
        transferOwnership(newBridge);
    }
}
