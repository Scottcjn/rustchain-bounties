// AgentFolioBeaconIntegration.sol
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

interface IBeacon {
    function verifyAgent(address agent, bytes32 dataHash, bytes calldata signature) external view returns (bool);
    function getAgentTrustScore(address agent) external view returns (uint256);
    function reportMalicious(address agent, string calldata reason) external;
}

interface IAgentFolio {
    function getAgentProfile(address agent) external view returns (string memory name, uint256 reputation, bool active);
    function stakeTokens(address agent, uint256 amount) external;
    function unstakeTokens(address agent, uint256 amount) external;
}

contract AgentFolioBeaconIntegration is Ownable, ReentrancyGuard {
    IBeacon public beacon;
    IAgentFolio public agentFolio;
    IERC20 public rtcToken;

    mapping(address => uint256) public agentStakes;
    mapping(address => uint256) public lastVerificationTime;
    mapping(address => bool) public verifiedAgents;

    uint256 public constant MIN_STAKE = 100 * 10**18; // 100 RTC
    uint256 public constant VERIFICATION_INTERVAL = 7 days;
    uint256 public constant TRUST_THRESHOLD = 70; // 70% trust score required

    event AgentVerified(address indexed agent, uint256 trustScore, uint256 timestamp);
    event AgentStaked(address indexed agent, uint256 amount);
    event AgentUnstaked(address indexed agent, uint256 amount);
    event MaliciousReported(address indexed reporter, address indexed agent, string reason);
    event TrustScoreUpdated(address indexed agent, uint256 newScore);

    constructor(address _beacon, address _agentFolio, address _rtcToken) {
        require(_beacon != address(0), "Invalid beacon address");
        require(_agentFolio != address(0), "Invalid agent folio address");
        require(_rtcToken != address(0), "Invalid RTC token address");

        beacon = IBeacon(_beacon);
        agentFolio = IAgentFolio(_agentFolio);
        rtcToken = IERC20(_rtcToken);
    }

    function verifyAndStake(address agent, bytes32 dataHash, bytes calldata signature) external nonReentrant {
        require(!verifiedAgents[agent], "Agent already verified");
        require(beacon.verifyAgent(agent, dataHash, signature), "Beacon verification failed");

        uint256 trustScore = beacon.getAgentTrustScore(agent);
        require(trustScore >= TRUST_THRESHOLD, "Trust score below threshold");

        (string memory name, uint256 reputation, bool active) = agentFolio.getAgentProfile(agent);
        require(active, "Agent not active in AgentFolio");

        // Stake minimum amount
        require(rtcToken.transferFrom(msg.sender, address(this), MIN_STAKE), "Token transfer failed");
        agentStakes[agent] = MIN_STAKE;
        agentFolio.stakeTokens(agent, MIN_STAKE);

        verifiedAgents[agent] = true;
        lastVerificationTime[agent] = block.timestamp;

        emit AgentVerified(agent, trustScore, block.timestamp);
        emit AgentStaked(agent, MIN_STAKE);
    }

    function refreshVerification(address agent) external nonReentrant {
        require(verifiedAgents[agent], "Agent not verified");
        require(block.timestamp >= lastVerificationTime[agent] + VERIFICATION_INTERVAL, "Verification not due");

        uint256 trustScore = beacon.getAgentTrustScore(agent);
        require(trustScore >= TRUST_THRESHOLD, "Trust score dropped below threshold");

        lastVerificationTime[agent] = block.timestamp;
        emit TrustScoreUpdated(agent, trustScore);
    }

    function unstake(address agent) external nonReentrant {
        require(verifiedAgents[agent], "Agent not verified");
        require(msg.sender == owner() || msg.sender == agent, "Unauthorized");

        uint256 stakeAmount = agentStakes[agent];
        require(stakeAmount > 0, "No stake to withdraw");

        agentStakes[agent] = 0;
        verifiedAgents[agent] = false;
        agentFolio.unstakeTokens(agent, stakeAmount);

        require(rtcToken.transfer(msg.sender, stakeAmount), "Token transfer failed");
        emit AgentUnstaked(agent, stakeAmount);
    }

    function reportMalicious(address agent, string calldata reason) external nonReentrant {
        require(verifiedAgents[agent], "Agent not verified");
        require(bytes(reason).length > 0, "Reason required");

        beacon.reportMalicious(agent, reason);
        emit MaliciousReported(msg.sender, agent, reason);

        // Auto-unstake on malicious report
        uint256 stakeAmount = agentStakes[agent];
        if (stakeAmount > 0) {
            agentStakes[agent] = 0;
            verifiedAgents[agent] = false;
            agentFolio.unstakeTokens(agent, stakeAmount);
            require(rtcToken.transfer(owner(), stakeAmount), "Token transfer failed");
        }
    }

    function getAgentStatus(address agent) external view returns (bool verified, uint256 stake, uint256 trustScore, uint256 lastVerification) {
        verified = verifiedAgents[agent];
        stake = agentStakes[agent];
        trustScore = beacon.getAgentTrustScore(agent);
        lastVerification = lastVerificationTime[agent];
    }

    function updateBeacon(address newBeacon) external onlyOwner {
        require(newBeacon != address(0), "Invalid beacon address");
        beacon = IBeacon(newBeacon);
    }

    function updateAgentFolio(address newAgentFolio) external onlyOwner {
        require(newAgentFolio != address(0), "Invalid agent folio address");
        agentFolio = IAgentFolio(newAgentFolio);
    }

    function emergencyWithdraw(address token, uint256 amount) external onlyOwner {
        IERC20(token).transfer(owner(), amount);
    }
}