// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title CrossChainMinter
 * @dev Mints wRTC on Base when tokens are locked on Solana
 */
contract CrossChainMinter is ERC20, Ownable, ReentrancyGuard {
    
    struct LockEvent {
        address user;
        uint256 amount;
        string sourceChain;
        bytes32 sourceTxHash;
        uint256 timestamp;
        bool claimed;
    }
    
    mapping(bytes32 => LockEvent) public lockEvents;
    mapping(address => uint256) public userPendingAmount;
    
    bytes32[] public allLockEvents;
    
    // Bridge operator addresses (LayerZero/Wormhole)
    mapping(address => bool) public authorizedBridges;
    
    event TokensMinted(address indexed user, uint256 amount, bytes32 indexed lockEventId, string sourceChain);
    event BridgeAuthorized(address bridge, bool authorized);
    event LockEventCreated(bytes32 indexed eventId, address indexed user, uint256 amount, string sourceChain);
    
    constructor() ERC20("Wrapped RTC", "wRTC") Ownable(msg.sender) {}
    
    /**
     * @dev Authorize a bridge contract
     */
    function authorizeBridge(address _bridge, bool _authorized) external onlyOwner {
        authorizedBridges[_bridge] = _authorized;
        emit BridgeAuthorized(_bridge, _authorized);
    }
    
    /**
     * @dev Create a lock event from Solana (called by bridge)
     */
    function createLockEvent(
        address _user,
        uint256 _amount,
        string calldata _sourceChain,
        bytes32 _sourceTxHash
    ) external returns (bytes32) {
        require(authorizedBridges[msg.sender], "Unauthorized bridge");
        require(_amount > 0, "Invalid amount");
        require(_user != address(0), "Invalid user");
        
        bytes32 eventId = keccak256(abi.encodePacked(
            _user,
            _amount,
            _sourceChain,
            _sourceTxHash,
            block.timestamp
        ));
        
        lockEvents[eventId] = LockEvent({
            user: _user,
            amount: _amount,
            sourceChain: _sourceChain,
            sourceTxHash: _sourceTxHash,
            timestamp: block.timestamp,
            claimed: false
        });
        
        allLockEvents.push(eventId);
        userPendingAmount[_user] += _amount;
        
        emit LockEventCreated(eventId, _user, _amount, _sourceChain);
        
        return eventId;
    }
    
    /**
     * @dev Claim minted tokens for a lock event
     */
    function claimTokens(bytes32 _eventId) external nonReentrant {
        LockEvent storage event_ = lockEvents[_eventId];
        
        require(event_.user == msg.sender, "Not your lock event");
        require(!event_.claimed, "Already claimed");
        require(block.timestamp >= event_.timestamp, "Invalid timestamp");
        
        uint256 amount = event_.amount;
        require(amount > 0, "Invalid amount");
        
        event_.claimed = true;
        userPendingAmount[msg.sender] -= amount;
        
        _mint(msg.sender, amount);
        
        emit TokensMinted(msg.sender, amount, _eventId, event_.sourceChain);
    }
    
    /**
     * @dev Burn tokens to unlock on Solana
     */
    function burnForUnlock(uint256 _amount, string calldata _solanaAddress) external returns (bytes32) {
        require(_amount > 0, "Invalid amount");
        require(balanceOf(msg.sender) >= _amount, "Insufficient balance");
        
        _burn(msg.sender, _amount);
        
        bytes32 burnEventId = keccak256(abi.encodePacked(
            msg.sender,
            _amount,
            _solanaAddress,
            block.timestamp
        ));
        
        emit TokensMinted(msg.sender, _amount, burnEventId, "Base");
        
        return burnEventId;
    }
    
    /**
     * @dev Get all lock events for a user
     */
    function getUserLockEvents(address _user) external view returns (bytes32[] memory) {
        uint256 count = 0;
        for (uint256 i = 0; i < allLockEvents.length; i++) {
            if (lockEvents[allLockEvents[i]].user == _user) {
                count++;
            }
        }
        
        bytes32[] memory result = new bytes32[](count);
        uint256 index = 0;
        for (uint256 i = 0; i < allLockEvents.length; i++) {
            if (lockEvents[allLockEvents[i]].user == _user) {
                result[index] = allLockEvents[i];
                index++;
            }
        }
        
        return result;
    }
    
    /**
     * @dev Get total pending amount for all users
     */
    function getTotalPending() external view returns (uint256) {
        return totalSupply();
    }
}
