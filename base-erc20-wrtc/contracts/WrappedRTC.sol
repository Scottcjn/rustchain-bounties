// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title WrappedRTC (wRTC) on Base
 * @dev ERC-20 token representing wrapped RTC on Base L2
 * @notice 6 decimal precision to match RTC native token
 */
contract WrappedRTC is ERC20, ERC20Burnable, Ownable {
    
    // Token metadata
    string private constant _name = "Wrapped RTC";
    string private constant _symbol = "wRTC";
    uint8 private constant _decimals = 6;
    
    // Bridge admin (can mint/burn)
    address public bridgeAdmin;
    
    // Bridge status
    bool public bridgePaused;
    
    // Anti-Sybil: minimum balance required
    uint256 public constant MIN_ETH_BALANCE = 0.01 ether;
    
    // Events
    event BridgeMint(address indexed to, uint256 amount, bytes32 lockTxHash);
    event BridgeBurn(address indexed from, uint256 amount, string recipient);
    event BridgePauseChanged(bool paused);
    event BridgeAdminChanged(address indexed newAdmin);
    
    // Custom errors
    error BridgePaused();
    error BelowMinimumBalance();
    error ZeroAmount();
    error InvalidRecipient();
    
    /**
     * @dev Constructor
     * @param initialOwner The initial owner (can transfer ownership to multisig)
     */
    constructor(address initialOwner) Ownable(initialOwner) ERC20(_name, _symbol) {
        bridgeAdmin = initialOwner;
        _mint(initialOwner, 0); // Start with 0 supply
    }
    
    /**
     * @dev Override decimals to match RTC (6 decimals)
     */
    function decimals() public pure override returns (uint8) {
        return _decimals;
    }
    
    /**
     * @dev Mint tokens (called by bridge when locking on source chain)
     * @param to Address to mint tokens to
     * @param amount Amount to mint
     * @param lockTxHash Hash of the lock transaction on source chain
     */
    function bridgeMint(address to, uint256 amount, bytes32 lockTxHash) external {
        if (msg.sender != bridgeAdmin) revert OwnableUnauthorizedAddress(msg.sender);
        if (to == address(0)) revert InvalidRecipient();
        if (amount == 0) revert ZeroAmount();
        if (bridgePaused) revert BridgePaused();
        
        _mint(to, amount);
        emit BridgeMint(to, amount, lockTxHash);
    }
    
    /**
     * @dev Burn tokens (called by bridge for unlocking on destination)
     * @param amount Amount to burn
     * @param recipient RTC wallet name of the recipient on source chain
     */
    function bridgeBurn(uint256 amount, string calldata recipient) external {
        if (amount == 0) revert ZeroAmount();
        if (bridgePaused) revert BridgePaused();
        if (bytes(recipient).length == 0) revert InvalidRecipient();
        
        // Anti-Sybil check: sender must have minimum ETH balance
        if (msg.sender.balance < MIN_ETH_BALANCE) revert BelowMinimumBalance();
        
        _burn(msg.sender, amount);
        emit BridgeBurn(msg.sender, amount, recipient);
    }
    
    /**
     * @dev Pause/unpause bridge operations
     * @param paused New pause status
     */
    function setBridgePaused(bool paused) external onlyOwner {
        bridgePaused = paused;
        emit BridgePauseChanged(paused);
    }
    
    /**
     * @dev Update bridge admin
     * @param newAdmin New bridge admin address
     */
    function setBridgeAdmin(address newAdmin) external onlyOwner {
        if (newAdmin == address(0)) revert InvalidRecipient();
        bridgeAdmin = newAdmin;
        emit BridgeAdminChanged(newAdmin);
    }
    
    /**
     * @dev Emergency withdraw (only owner)
     * @param token Token to withdraw
     * @param amount Amount to withdraw
     */
    function emergencyWithdraw(IERC20 token, uint256 amount) external onlyOwner {
        token.transfer(owner(), amount);
    }
}
