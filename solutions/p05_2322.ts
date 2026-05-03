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
        bool hasCRT;
        bool hasOriginalController;
        uint256 rewardClaimed;
        uint256 timestamp;
    }

    Submission[] public submissions;
    mapping(address => uint256) public pendingRewards;
    mapping(address => bool) public hasSubmitted;

    event SubmissionAdded(
        uint256 indexed submissionId,
        address indexed submitter,
        string photoUrl,
        string description,
        bool hasCRT,
        bool hasOriginalController,
        uint256 timestamp
    );

    event RewardClaimed(address indexed claimant, uint256 amount);

    constructor(address _rtcToken) {
        require(_rtcToken != address(0), "Invalid token address");
        rtcToken = IERC20(_rtcToken);
    }

    function submitEntry(
        string memory _photoUrl,
        string memory _description,
        bool _hasCRT,
        bool _hasOriginalController
    ) external {
        require(bytes(_photoUrl).length > 0, "Photo URL required");
        require(bytes(_description).length > 0, "Description required");
        require(!hasSubmitted[msg.sender], "Already submitted");

        uint256 reward = BASE_REWARD;
        if (_hasCRT) reward += CRT_BONUS;
        if (_hasOriginalController) reward += ORIGINAL_CONTROLLER_BONUS;

        submissions.push(Submission({
            submitter: msg.sender,
            photoUrl: _photoUrl,
            description: _description,
            hasCRT: _hasCRT,
            hasOriginalController: _hasOriginalController,
            rewardClaimed: 0,
            timestamp: block.timestamp
        }));

        hasSubmitted[msg.sender] = true;
        pendingRewards[msg.sender] = reward;

        emit SubmissionAdded(
            submissions.length - 1,
            msg.sender,
            _photoUrl,
            _description,
            _hasCRT,
            _hasOriginalController,
            block.timestamp
        );
    }

    function claimReward() external {
        uint256 reward = pendingRewards[msg.sender];
        require(reward > 0, "No pending reward");
        require(rtcToken.balanceOf(address(this)) >= reward, "Insufficient contract balance");

        pendingRewards[msg.sender] = 0;
        require(rtcToken.transfer(msg.sender, reward), "Transfer failed");

        emit RewardClaimed(msg.sender, reward);
    }

    function getSubmissionCount() external view returns (uint256) {
        return submissions.length;
    }

    function getSubmission(uint256 _index) external view returns (
        address submitter,
        string memory photoUrl,
        string memory description,
        bool hasCRT,
        bool hasOriginalController,
        uint256 rewardClaimed,
        uint256 timestamp
    ) {
        require(_index < submissions.length, "Invalid index");
        Submission storage s = submissions[_index];
        return (
            s.submitter,
            s.photoUrl,
            s.description,
            s.hasCRT,
            s.hasOriginalController,
            s.rewardClaimed,
            s.timestamp
        );
    }

    function getPendingReward(address _user) external view returns (uint256) {
        return pendingRewards[_user];
    }

    function depositRewards(uint256 _amount) external onlyOwner {
        require(rtcToken.transferFrom(msg.sender, address(this), _amount), "Transfer failed");
    }

    function withdrawRemaining() external onlyOwner {
        uint256 balance = rtcToken.balanceOf(address(this));
        require(balance > 0, "No balance");
        require(rtcToken.transfer(owner(), balance), "Transfer failed");
    }
}