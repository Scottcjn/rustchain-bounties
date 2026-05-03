// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract RetroScreenshotGallery is Ownable {
    IERC20 public rtcToken;
    uint256 public constant BASE_REWARD = 1 ether; // 1 RTC
    uint256 public constant CRT_BONUS = 1 ether;
    uint256 public constant ORIGINAL_CONTROLLER_BONUS = 1 ether;

    struct Submission {
        address submitter;
        string photoUrl;
        string description;
        bool hasCrt;
        bool hasOriginalController;
        uint256 reward;
        bool rewarded;
    }

    Submission[] public submissions;
    mapping(address => uint256) public submissionCount;

    event SubmissionAdded(
        uint256 indexed submissionId,
        address indexed submitter,
        string photoUrl,
        string description,
        bool hasCrt,
        bool hasOriginalController
    );

    event RewardPaid(
        uint256 indexed submissionId,
        address indexed submitter,
        uint256 amount
    );

    constructor(address _rtcToken) {
        require(_rtcToken != address(0), "Invalid token address");
        rtcToken = IERC20(_rtcToken);
    }

    function submitScreenshot(
        string memory _photoUrl,
        string memory _description,
        bool _hasCrt,
        bool _hasOriginalController
    ) external {
        require(bytes(_photoUrl).length > 0, "Photo URL required");
        require(bytes(_description).length > 0, "Description required");

        uint256 reward = BASE_REWARD;
        if (_hasCrt) reward += CRT_BONUS;
        if (_hasOriginalController) reward += ORIGINAL_CONTROLLER_BONUS;

        submissions.push(Submission({
            submitter: msg.sender,
            photoUrl: _photoUrl,
            description: _description,
            hasCrt: _hasCrt,
            hasOriginalController: _hasOriginalController,
            reward: reward,
            rewarded: false
        }));

        submissionCount[msg.sender]++;

        emit SubmissionAdded(
            submissions.length - 1,
            msg.sender,
            _photoUrl,
            _description,
            _hasCrt,
            _hasOriginalController
        );
    }

    function rewardSubmission(uint256 _submissionId) external onlyOwner {
        require(_submissionId < submissions.length, "Invalid submission ID");
        Submission storage submission = submissions[_submissionId];
        require(!submission.rewarded, "Already rewarded");

        uint256 reward = submission.reward;
        require(rtcToken.transfer(submission.submitter, reward), "Transfer failed");

        submission.rewarded = true;

        emit RewardPaid(_submissionId, submission.submitter, reward);
    }

    function getSubmission(uint256 _submissionId) external view returns (
        address submitter,
        string memory photoUrl,
        string memory description,
        bool hasCrt,
        bool hasOriginalController,
        uint256 reward,
        bool rewarded
    ) {
        require(_submissionId < submissions.length, "Invalid submission ID");
        Submission storage s = submissions[_submissionId];
        return (
            s.submitter,
            s.photoUrl,
            s.description,
            s.hasCrt,
            s.hasOriginalController,
            s.reward,
            s.rewarded
        );
    }

    function getSubmissionCount() external view returns (uint256) {
        return submissions.length;
    }

    function withdrawTokens() external onlyOwner {
        uint256 balance = rtcToken.balanceOf(address(this));
        require(balance > 0, "No tokens to withdraw");
        require(rtcToken.transfer(owner(), balance), "Transfer failed");
    }
}