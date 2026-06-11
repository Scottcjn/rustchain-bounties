// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title RustChainRegistry
 * @dev A smart contract to store bounties, node states, and balances.
 *      This contract serves as the on-chain backend for AI Agent tools (CrewAI, AutoGen, etc.).
 *      The Python tools will interact with this contract via Web3.py.
 */
contract RustChainRegistry {
    
    struct Bounty {
        uint256 id;
        string title;
        string description;
        uint256 rewardAmount;
        string status; // "OPEN", "IN_PROGRESS", "COMPLETED"
        address creator;
        uint256 createdAt;
    }

    struct NodeState {
        address nodeAddress;
        string status; // "ACTIVE", "OFFLINE", "SYNCING"
        uint256 lastHeartbeat;
        uint256 totalBlocksProcessed;
    }

    mapping(uint256 => Bounty) public bounties;
    mapping(address => NodeState) public nodes;
    mapping(address => uint256) public balances;
    
    uint256 public bountyCount;

    event BountyCreated(uint256 indexed id, string title, uint256 reward);
    event NodeRegistered(address indexed nodeAddress, string status);
    event Heartbeat(address indexed nodeAddress, uint256 timestamp);
    event RewardClaimed(address indexed user, uint256 amount);

    constructor() {
        // Initialize with a dummy bounty for testing
        _createBounty("Welcome Bounty", "First bounty on RustChain", 1000);
    }

    /**
     * @dev Creates a new bounty.
     */
    function createBounty(string memory _title, string memory _description, uint256 _reward) external payable {
        require(msg.value >= _reward, "Insufficient funds sent");
        _createBounty(_title, _description, _reward);
    }

    function _createBounty(string memory _title, string memory _description, uint256 _reward) internal {
        bountyCount++;
        bounties[bountyCount] = Bounty({
            id: bountyCount,
            title: _title,
            description: _description,
            rewardAmount: _reward,
            status: "OPEN",
            creator: msg.sender,
            createdAt: block.timestamp
        });
        emit BountyCreated(bountyCount, _title, _reward);
    }

    /**
     * @dev Registers a node or updates its heartbeat.
     */
    function registerNode(string memory _status) external {
        NodeState storage node = nodes[msg.sender];
        node.nodeAddress = msg.sender;
        node.status = _status;
        node.lastHeartbeat = block.timestamp;
        node.totalBlocksProcessed = 0; // Reset or increment logic based on real needs
        
        if (node.totalBlocksProcessed == 0) {
            emit NodeRegistered(msg.sender, _status);
        } else {
            emit Heartbeat(msg.sender, block.timestamp);
        }
    }

    /**
     * @dev Updates node heartbeat.
     */
    function heartbeat() external {
        require(nodes[msg.sender].nodeAddress != address(0), "Node not registered");
        nodes[msg.sender].lastHeartbeat = block.timestamp;
        nodes[msg.sender].totalBlocksProcessed++;
        emit Heartbeat(msg.sender, block.timestamp);
    }

    /**
     * @dev Returns a specific bounty by ID.
     */
    function getBounty(uint256 _id) external view returns (
        uint256 id,
        string memory title,
        string memory description,
        uint256 rewardAmount,
        string memory status,
        address creator,
        uint256 createdAt
    ) {
        require(_id > 0 && _id <= bountyCount, "Bounty not found");
        Bounty memory b = bounties[_id];
        return (b.id, b.title, b.description, b.rewardAmount, b.status, b.creator, b.createdAt);
    }

    /**
     * @dev Returns the list of all bounty IDs (simplified for agent iteration).
     */
    function getAllBountyIds() external view returns (uint256[] memory) {
        uint256[] memory ids = new uint256[](bountyCount);
        for (uint256 i = 1; i <= bountyCount; i++) {
            ids[i-1] = i;
        }
        return ids;
    }

    /**
     * @dev Returns node state for an address.
     */
    function getNodeState(address _node) external view returns (
        address nodeAddress,
        string memory status,
        uint256 lastHeartbeat,
        uint256 totalBlocksProcessed
    ) {
        NodeState memory n = nodes[_node];
        return (n.nodeAddress, n.status, n.lastHeartbeat, n.totalBlocksProcessed);
    }

    /**
     * @dev Returns the balance of a user.
     */
    function getBalance(address _user) external view returns (uint256) {
        return balances[_user];
    }

    /**
     * @dev Internal helper to update balance (mocking reward distribution).
     */
    function distributeReward(address _to, uint256 _amount) external {
        // In a real scenario, this would be restricted to an admin or DAO
        balances[_to] += _amount;
        emit RewardClaimed(_to, _amount);
    }
}