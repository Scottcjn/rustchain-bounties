// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract RetroScreenshotGallery {
    address public owner;
    uint256 public totalSubmissions;
    uint256 public constant SUBMISSION_FEE = 0.01 ether;
    uint256 public constant REWARD_AMOUNT = 1 ether; // 1 RTC token equivalent

    struct Submission {
        uint256 id;
        address submitter;
        string photoUrl;
        string description;
        bool hasCRT;
        bool hasOriginalController;
        uint256 timestamp;
        bool rewarded;
    }

    mapping(uint256 => Submission) public submissions;
    mapping(address => uint256[]) public userSubmissions;

    event SubmissionCreated(
        uint256 indexed id,
        address indexed submitter,
        string photoUrl,
        string description,
        bool hasCRT,
        bool hasOriginalController,
        uint256 timestamp
    );

    event RewardPaid(
        uint256 indexed submissionId,
        address indexed submitter,
        uint256 amount
    );

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function submitScreenshot(
        string memory _photoUrl,
        string memory _description,
        bool _hasCRT,
        bool _hasOriginalController
    ) public payable {
        require(msg.value >= SUBMISSION_FEE, "Insufficient submission fee");
        require(bytes(_photoUrl).length > 0, "Photo URL required");
        require(bytes(_description).length > 0, "Description required");

        totalSubmissions++;
        uint256 submissionId = totalSubmissions;

        submissions[submissionId] = Submission({
            id: submissionId,
            submitter: msg.sender,
            photoUrl: _photoUrl,
            description: _description,
            hasCRT: _hasCRT,
            hasOriginalController: _hasOriginalController,
            timestamp: block.timestamp,
            rewarded: false
        });

        userSubmissions[msg.sender].push(submissionId);

        emit SubmissionCreated(
            submissionId,
            msg.sender,
            _photoUrl,
            _description,
            _hasCRT,
            _hasOriginalController,
            block.timestamp
        );
    }

    function rewardSubmission(uint256 _submissionId) public onlyOwner {
        require(_submissionId > 0 && _submissionId <= totalSubmissions, "Invalid submission ID");
        Submission storage submission = submissions[_submissionId];
        require(!submission.rewarded, "Already rewarded");

        uint256 rewardAmount = REWARD_AMOUNT;
        if (submission.hasCRT) {
            rewardAmount += 1 ether; // +1 RTC for CRT
        }
        if (submission.hasOriginalController) {
            rewardAmount += 1 ether; // +1 RTC for original controller
        }

        submission.rewarded = true;
        payable(submission.submitter).transfer(rewardAmount);

        emit RewardPaid(_submissionId, submission.submitter, rewardAmount);
    }

    function getSubmission(uint256 _submissionId) public view returns (
        uint256 id,
        address submitter,
        string memory photoUrl,
        string memory description,
        bool hasCRT,
        bool hasOriginalController,
        uint256 timestamp,
        bool rewarded
    ) {
        Submission storage s = submissions[_submissionId];
        return (
            s.id,
            s.submitter,
            s.photoUrl,
            s.description,
            s.hasCRT,
            s.hasOriginalController,
            s.timestamp,
            s.rewarded
        );
    }

    function getUserSubmissions(address _user) public view returns (uint256[] memory) {
        return userSubmissions[_user];
    }

    function withdrawFees() public onlyOwner {
        payable(owner).transfer(address(this).balance);
    }
}