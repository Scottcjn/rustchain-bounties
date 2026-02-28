```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title RetroactiveImpactRewards
 * @author The Unsung Hero Developer
 * @notice Solves the "mercenary" culture of traditional bounties by allowing
 * peer-driven, retroactive surprise bonuses for critical but unglamorous work.
 */
contract RetroactiveImpactRewards {
    // Treasury backing the retroactive impact program
    address public immutable PROGRAM_TREASURY = 0xeDD46E3D9680b676e53c19A2089A05313c6fD5F9;
    address public committee;

    enum Category { ObscureBugFix, Mentorship, Documentation, Infrastructure, Support, Other }
    enum Status { Pending, Rewarded, Rejected }

    struct Nomination {
        address nominee;
        address nominator;
        Category category;
        string description;
        Status status;
        uint256 rewardAmount;
    }

    uint256 public nominationCount;
    mapping(uint256 => Nomination) public nominations;

    event UnsungHeroNominated(uint256 indexed id, address indexed nominee, Category category, string description);
    event SurpriseBonusAwarded(uint256 indexed id, address indexed hero, uint256 amount);
    event NominationRejected(uint256 indexed id, string reason);

    modifier onlyCommittee() {
        require(msg.sender == committee || msg.sender == PROGRAM_TREASURY, "Not authorized to allocate funds");
        _;
    }

    constructor() {
        committee = msg.sender;
    }

    // Contract can receive funds from benefactors wanting to sponsor unsung heroes
    receive() external payable {}

    /**
     * @notice Nominate an unsung hero for the invisible value they created.
     * @param _nominee The developer who did the unglamorous work.
     * @param _category The type of work completed (docs, mentorship, etc.).
     * @param _description Git commit, PR link, or explanation of impact.
     */
    function nominateHero(
        address _nominee,
        Category _category,
        string calldata _description
    ) external returns (uint256) {
        require(_nominee != address(0), "Invalid nominee address");
        require(_nominee != msg.sender, "Cannot nominate yourself");

        uint256 id = ++nominationCount;
        nominations[id] = Nomination({
            nominee: _nominee,
            nominator: msg.sender,
            category: _category,
            description: _description,
            status: Status.Pending,
            rewardAmount: 0
        });

        emit UnsungHeroNominated(id, _nominee, _category, _description);
        return id;
    }

    /**
     * @notice Distribute a retroactive surprise bonus to a nominated hero.
     * @param _nominationId The ID of the peer nomination.
     */
    function awardSurpriseBonus(uint256 _nominationId) external payable onlyCommittee {
        Nomination storage nom = nominations[_nominationId];
        require(nom.status == Status.Pending, "Nomination already processed");

        uint256 reward = msg.value;
        require(reward > 0 || address(this).balance >= reward, "Insufficient reward funding");

        nom.status = Status.Rewarded;
        nom.rewardAmount = reward;

        (bool success, ) = nom.nominee.call{value: reward}("");
        require(success, "Reward transfer failed");

        emit SurpriseBonusAwarded(_nominationId, nom.nominee, reward);
    }

    /**
     * @notice Batch process multiple unsung heroes to save gas and distribute treasury funds.
     */
    function batchAwardSurpriseBonuses(
        uint256[] calldata _nominationIds,
        uint256[] calldata _amounts
    ) external payable onlyCommittee {
        require(_nominationIds.length == _amounts.length, "Mismatched input arrays");

        for(uint256 i = 0; i < _nominationIds.length; i++) {
            Nomination storage nom = nominations[_nominationIds[i]];

            if(nom.status == Status.Pending) {
                nom.status = Status.Rewarded;
                nom.rewardAmount = _amounts[i];

                (bool success, ) = nom.nominee.call{value: _amounts[i]}("");
                require(success, "Reward transfer failed");

                emit SurpriseBonusAwarded(_nominationIds[i], nom.nominee, _amounts[i]);
            }
        }
    }

    /**
     * @notice Reject a nomination if it is deemed invalid or spam.
     */
    function rejectNomination(uint256 _nominationId, string calldata _reason) external onlyCommittee {
        Nomination storage nom = nominations[_nominationId];
        require(nom.status == Status.Pending, "Nomination already processed");

        nom.status = Status.Rejected;
        emit NominationRejected(_nominationId, _reason);
    }
}
```