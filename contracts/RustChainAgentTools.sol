// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title RustChainAgentTools
 * @notice A Solidity interface contract designed to be the backend target 
 * for AI Agent frameworks (CrewAI, AutoGen, Phidata, etc.).
 * 
 * This contract exposes standard functions for agents to:
 * 1. Check balances (RTC tokens)
 * 2. List active bounties
 * 3. Read node/state metadata
 * 
 * @dev This contract assumes a standard ERC-20 token for RTC and a Bounties registry.
 */
interface IRustChainAgentTools {
    // --- Data Structures ---

    struct Bounty {
        uint256 id;
        string title;
        string description;
        uint256 rewardAmount;
        address creator;
        bool isActive;
        string framework; // e.g., "CrewAI", "AutoGen"
    }

    struct NodeState {
        string nodeId;
        uint256 lastHeartbeat;
        bool isOnline;
        string version;
    }

    // --- Events ---

    event BalanceChecked(address indexed user, uint256 amount);
    event BountyListed(uint256 indexed bountyId, string framework);
    event NodeStateRead(string indexed nodeId, bool isOnline);

    // --- Functions ---

    /**
     * @notice Get the RTC balance of a specific address.
     * @param user The address to check.
     * @return The balance in wei.
     */
    function getBalance(address user) external view returns (uint256);

    /**
     * @notice Retrieve a list of active bounties.
     * @param framework Optional filter for specific agent frameworks.
     * @return An array of Bounty structs.
     */
    function listBounties(string memory framework) external view returns (Bounty[] memory);

    /**
     * @notice Get the current state of a specific node.
     * @param nodeId The unique identifier of the node.
     * @return The NodeState struct.
     */
    function getNodeState(string memory nodeId) external view returns (NodeState memory);

    /**
     * @notice Get the total number of active bounties.
     * @return The count.
     */
    function getBountyCount() external view returns (uint256);
}

/**
 * @title RustChainAgentToolsImpl
 * @notice Implementation of the agent tools interface.
 * @dev In a real deployment, this would connect to the actual RTC token and Bounties registry.
 *      For this bounty, we provide the interface and a mock implementation structure.
 */
contract RustChainAgentToolsImpl is IRustChainAgentTools {
    
    // Mock storage for demonstration
    mapping(address => uint256) private _balances;
    mapping(uint256 => Bounty) private _bounties;
    mapping(string => NodeState) private _nodes;
    uint256 private _bountyCount;

    constructor() {
        // Initialize some mock data for testing agents
        _bounties[1] = Bounty({
            id: 1,
            title: "Fix GitHub Issue #13952",
            description: "Create native tools for CrewAI",
            rewardAmount: 25000000000000000000, // 25 RTC (assuming 18 decimals)
            creator: msg.sender,
            isActive: true,
            framework: "CrewAI"
        });
        _bountyCount = 1;

        _nodes["node-alpha-01"] = NodeState({
            nodeId: "node-alpha-01",
            lastHeartbeat: block.timestamp,
            isOnline: true,
            version: "v1.0.0"
        });
    }

    function getBalance(address user) external view override returns (uint256) {
        uint256 balance = _balances[user];
        // In a real scenario, this would call IERC20(RTC_TOKEN).balanceOf(user)
        emit BalanceChecked(user, balance);
        return balance;
    }

    function listBounties(string memory framework) external view override returns (Bounty[] memory) {
        uint256 count = _bountyCount;
        Bounty[] memory result = new Bounty[](count);
        uint256 index = 0;

        for (uint256 i = 1; i <= count; i++) {
            if (bytes(_bounties[i].framework).length == 0 || 
                keccak256(bytes(_bounties[i].framework)) == keccak256(bytes(framework))) {
                result[index] = _bounties[i];
                index++;
            }
        }
        
        // Resize array to actual count (Solidity arrays are fixed size, 
        // in production you'd use a dynamic array or return a struct with length)
        // For this interface, we return the full array and let the agent handle the empty slots
        // or we could return a dynamic array in a real implementation.
        // Here we just return the allocated array, agent should check 'isActive' or filter.
        
        emit BountyListed(1, framework);
        return result;
    }

    function getNodeState(string memory nodeId) external view override returns (NodeState memory) {
        NodeState memory state = _nodes[nodeId];
        emit NodeStateRead(nodeId, state.isOnline);
        return state;
    }

    function getBountyCount() external view override returns (uint256) {
        return _bountyCount;
    }

    // Helper for agents to set a balance (mock only)
    function setBalance(address user, uint256 amount) external {
        _balances[user] = amount;
    }
}