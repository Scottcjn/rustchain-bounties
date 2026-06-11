// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract BountyContract {
    // Mapping of bounty IDs to their respective claim status
    mapping(uint256 => bool) public bountyClaims;

    // Function to claim a bounty
    function claimBounty(uint256 _bountyId) public {
        // Check if the bounty has already been claimed
        require(!bountyClaims[_bountyId], "Bounty already claimed");

        // Mark the bounty as claimed
        bountyClaims[_bountyId] = true;

        // Emit an event to notify of the claim
        emit BountyClaimed(_bountyId, msg.sender);
    }

    // Event emitted when a bounty is claimed
    event BountyClaimed(uint256 indexed bountyId, address indexed claimant);
}