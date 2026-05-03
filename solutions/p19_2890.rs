// AgentFolioBeaconIntegration.sol
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

interface IBeacon {
    function verifyTrust(bytes32 trustHash, bytes calldata signature) external view returns (bool);
    function getTrustLevel(address agent) external view returns (uint256);
}

interface IAgentFolio {
    function getAgentProfile(address agent) external view returns (string memory, uint256, bool);
    function updateTrustScore(address agent, uint256 score) external;
}

contract AgentFolioBeaconIntegration is Ownable, ReentrancyGuard {
    IBeacon public beacon;
    IAgentFolio public agentFolio;
    IERC20 public rewardToken;
    
    mapping(address => uint256) public trustScores;
    mapping(address => uint256) public lastUpdate;
    mapping(bytes32 => bool) public processedHashes;
    
    uint256 public constant MIN_TRUST_THRESHOLD = 70;
    uint256 public constant UPDATE_COOLDOWN = 1 hours;
    uint256 public constant REWARD_AMOUNT = 100 * 10**18; // 100 RTC
    
    event TrustVerified(address indexed agent, uint256 score, bytes32 trustHash);
    event TrustUpdated(address indexed agent, uint256 newScore);
    event RewardClaimed(address indexed agent, uint256 amount);
    
    constructor(address _beacon, address _agentFolio, address _rewardToken) {
        require(_beacon != address(0), "Invalid beacon address");
        require(_agentFolio != address(0), "Invalid agent folio address");
        require(_rewardToken != address(0), "Invalid reward token address");
        
        beacon = IBeacon(_beacon);
        agentFolio = IAgentFolio(_agentFolio);
        rewardToken = IERC20(_rewardToken);
    }
    
    function verifyAndUpdateTrust(address agent, bytes calldata signature) external nonReentrant returns (bool) {
        require(agent != address(0), "Invalid agent address");
        require(block.timestamp >= lastUpdate[agent] + UPDATE_COOLDOWN, "Cooldown active");
        
        bytes32 trustHash = keccak256(abi.encodePacked(agent, block.timestamp));
        require(!processedHashes[trustHash], "Hash already processed");
        
        bool verified = beacon.verifyTrust(trustHash, signature);
        require(verified, "Trust verification failed");
        
        uint256 beaconTrustLevel = beacon.getTrustLevel(agent);
        require(beaconTrustLevel >= MIN_TRUST_THRESHOLD, "Below minimum trust threshold");
        
        processedHashes[trustHash] = true;
        trustScores[agent] = beaconTrustLevel;
        lastUpdate[agent] = block.timestamp;
        
        agentFolio.updateTrustScore(agent, beaconTrustLevel);
        
        emit TrustVerified(agent, beaconTrustLevel, trustHash);
        emit TrustUpdated(agent, beaconTrustLevel);
        
        return true;
    }
    
    function claimReward(address agent) external nonReentrant returns (bool) {
        require(trustScores[agent] >= MIN_TRUST_THRESHOLD, "Below minimum trust threshold");
        require(rewardToken.balanceOf(address(this)) >= REWARD_AMOUNT, "Insufficient reward balance");
        
        trustScores[agent] = 0; // Reset to prevent double claim
        require(rewardToken.transfer(agent, REWARD_AMOUNT), "Reward transfer failed");
        
        emit RewardClaimed(agent, REWARD_AMOUNT);
        
        return true;
    }
    
    function getAgentTrustScore(address agent) external view returns (uint256) {
        return trustScores[agent];
    }
    
    function isTrustedAgent(address agent) external view returns (bool) {
        return trustScores[agent] >= MIN_TRUST_THRESHOLD;
    }
    
    function setBeacon(address _beacon) external onlyOwner {
        require(_beacon != address(0), "Invalid beacon address");
        beacon = IBeacon(_beacon);
    }
    
    function setAgentFolio(address _agentFolio) external onlyOwner {
        require(_agentFolio != address(0), "Invalid agent folio address");
        agentFolio = IAgentFolio(_agentFolio);
    }
    
    function setRewardToken(address _rewardToken) external onlyOwner {
        require(_rewardToken != address(0), "Invalid reward token address");
        rewardToken = IERC20(_rewardToken);
    }
    
    function setMinTrustThreshold(uint256 _threshold) external onlyOwner {
        require(_threshold > 0 && _threshold <= 100, "Invalid threshold");
        MIN_TRUST_THRESHOLD = _threshold;
    }
    
    function withdrawRewards(address to, uint256 amount) external onlyOwner {
        require(to != address(0), "Invalid address");
        require(amount > 0, "Amount must be greater than 0");
        require(rewardToken.balanceOf(address(this)) >= amount, "Insufficient balance");
        require(rewardToken.transfer(to, amount), "Transfer failed");
    }
    
    function depositRewards(uint256 amount) external onlyOwner {
        require(amount > 0, "Amount must be greater than 0");
        require(rewardToken.transferFrom(msg.sender, address(this), amount), "Transfer failed");
    }
}