// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";

interface IBeacon {
    function getImplementation(address _contract) external view returns (address);
    function upgradeTo(address _newImplementation) external;
}

interface IAgentFolio {
    function getAgent(address _agent) external view returns (Agent memory);
    function verifyAgent(address _agent, bytes calldata _signature) external returns (bool);
    function stake(address _agent, uint256 _amount) external;
    function unstake(address _agent, uint256 _amount) external;
    function slash(address _agent, uint256 _amount) external;
}

struct Agent {
    address agentAddress;
    string metadata;
    uint256 stake;
    uint256 reputation;
    bool active;
    uint256 lastUpdate;
}

struct TrustProof {
    address agent;
    uint256 timestamp;
    bytes signature;
    uint256 nonce;
}

contract AgentFolioBeaconIntegration is Ownable, ReentrancyGuard, EIP712 {
    using ECDSA for bytes32;

    // Constants
    bytes32 public constant TRUST_PROOF_TYPEHASH = keccak256(
        "TrustProof(address agent,uint256 timestamp,uint256 nonce)"
    );

    // State variables
    IBeacon public beacon;
    IAgentFolio public agentFolio;
    IERC20 public rtcToken;

    // Mappings
    mapping(address => bool) public registeredAgents;
    mapping(address => uint256) public agentNonces;
    mapping(address => TrustProof) public latestTrustProof;
    mapping(address => uint256) public agentReputation;

    // Events
    event AgentRegistered(address indexed agent, string metadata);
    event AgentUnregistered(address indexed agent);
    event TrustProofSubmitted(address indexed agent, uint256 timestamp, uint256 nonce);
    event ReputationUpdated(address indexed agent, uint256 newReputation);
    event StakeDeposited(address indexed agent, uint256 amount);
    event StakeWithdrawn(address indexed agent, uint256 amount);
    event SlashExecuted(address indexed agent, uint256 amount, string reason);
    event BeaconUpgraded(address indexed newBeacon);

    // Errors
    error AgentNotRegistered(address agent);
    error AgentAlreadyRegistered(address agent);
    error InvalidSignature();
    error InsufficientStake();
    error ExpiredProof();
    error NonceMismatch();

    constructor(
        address _beacon,
        address _agentFolio,
        address _rtcToken
    ) EIP712("AgentFolioBeaconIntegration", "1") {
        require(_beacon != address(0), "Invalid beacon address");
        require(_agentFolio != address(0), "Invalid agent folio address");
        require(_rtcToken != address(0), "Invalid RTC token address");

        beacon = IBeacon(_beacon);
        agentFolio = IAgentFolio(_agentFolio);
        rtcToken = IERC20(_rtcToken);
    }

    // Modifiers
    modifier onlyRegisteredAgent(address _agent) {
        if (!registeredAgents[_agent]) revert AgentNotRegistered(_agent);
        _;
    }

    modifier onlyUnregisteredAgent(address _agent) {
        if (registeredAgents[_agent]) revert AgentAlreadyRegistered(_agent);
        _;
    }

    // Core Functions

    function registerAgent(
        address _agent,
        string calldata _metadata,
        bytes calldata _signature
    ) external onlyUnregisteredAgent(_agent) {
        // Verify agent ownership via signature
        bytes32 digest = _hashTypedDataV4(
            keccak256(
                abi.encode(
                    TRUST_PROOF_TYPEHASH,
                    _agent,
                    block.timestamp,
                    agentNonces[_agent]
                )
            )
        );

        address signer = ECDSA.recover(digest, _signature);
        require(signer == _agent, "Invalid agent signature");

        // Register in AgentFolio
        agentFolio.verifyAgent(_agent, _signature);

        // Update state
        registeredAgents[_agent] = true;
        agentNonces[_agent]++;

        emit AgentRegistered(_agent, _metadata);
    }

    function unregisterAgent(address _agent) external onlyRegisteredAgent(_agent) {
        require(msg.sender == _agent || msg.sender == owner(), "Unauthorized");

        registeredAgents[_agent] = false;
        emit AgentUnregistered(_agent);
    }

    function submitTrustProof(
        address _agent,
        uint256 _timestamp,
        bytes calldata _signature
    ) external onlyRegisteredAgent(_agent) {
        if (block.timestamp - _timestamp > 1 hours) revert ExpiredProof();

        bytes32 digest = _hashTypedDataV4(
            keccak256(
                abi.encode(
                    TRUST_PROOF_TYPEHASH,
                    _agent,
                    _timestamp,
                    agentNonces[_agent]
                )
            )
        );

        address signer = ECDSA.recover(digest, _signature);
        if (signer != _agent) revert InvalidSignature();

        // Update trust proof
        latestTrustProof[_agent] = TrustProof({
            agent: _agent,
            timestamp: _timestamp,
            signature: _signature,
            nonce: agentNonces[_agent]
        });

        agentNonces[_agent]++;

        // Update reputation based on proof freshness
        _updateReputation(_agent);

        emit TrustProofSubmitted(_agent, _timestamp, agentNonces[_agent] - 1);
    }

    function depositStake(address _agent, uint256 _amount) external nonReentrant {
        require(_amount > 0, "Amount must be greater than 0");
        require(rtcToken.transferFrom(msg.sender, address(this), _amount), "Transfer failed");

        agentFolio.stake(_agent, _amount);
        emit StakeDeposited(_agent, _amount);
    }

    function withdrawStake(address _agent, uint256 _amount) external nonReentrant {
        require(msg.sender == _agent || msg.sender == owner(), "Unauthorized");
        require(_amount > 0, "Amount must be greater than 0");

        agentFolio.unstake(_agent, _amount);
        require(rtcToken.transfer(_agent, _amount), "Transfer failed");

        emit StakeWithdrawn(_agent, _amount);
    }

    function slashAgent(
        address _agent,
        uint256 _amount,
        string calldata _reason
    ) external onlyOwner {
        require(registeredAgents[_agent], "Agent not registered");
        require(_amount > 0, "Amount must be greater than 0");

        agentFolio.slash(_agent, _amount);

        // Update reputation negatively
        uint256 currentRep = agentReputation[_agent];
        uint256 penalty = _amount / 1e18; // 1 RTC = 1 reputation point penalty
        agentReputation[_agent] = currentRep > penalty ? currentRep - penalty : 0;

        emit SlashExecuted(_agent, _amount, _reason);
        emit ReputationUpdated(_agent, agentReputation[_agent]);
    }

    // Beacon Integration

    function upgradeBeacon(address _newBeacon) external onlyOwner {
        require(_newBeacon != address(0), "Invalid beacon address");
        beacon.upgradeTo(_newBeacon);
        beacon = IBeacon(_newBeacon);
        emit BeaconUpgraded(_newBeacon);
    }

    function getBeaconImplementation(address _contract) external view returns (address) {
        return beacon.getImplementation(_contract);
    }

    // Internal Functions

    function _updateReputation(address _agent) internal {
        TrustProof memory proof = latestTrustProof[_agent];
        uint256 timeSinceProof = block.timestamp - proof.timestamp;

        // Reputation calculation: higher reputation for recent proofs
        uint256 baseReputation = 100;
        uint256 timeDecay = timeSinceProof / 1 hours;

        if (timeDecay == 0) {
            agentReputation[_agent] = baseReputation;
        } else {
            uint256 decayed = baseReputation / (timeDecay + 1);
            agentReputation[_agent] = decayed;
        }

        emit ReputationUpdated(_agent, agentReputation[_agent]);
    }

    // View Functions

    function getAgentReputation(address _agent) external view returns (uint256) {
        return agentReputation[_agent];
    }

    function getAgentNonce(address _agent) external view returns (uint256) {
        return agentNonces[_agent];
    }

    function getLatestTrustProof(address _agent) external view returns (TrustProof memory) {
        return latestTrustProof[_agent];
    }

    function isAgentRegistered(address _agent) external view returns (bool) {
        return registeredAgents[_agent];
    }

    // Recovery function for stuck tokens
    function recoverTokens(address _token, uint256 _amount) external onlyOwner {
        IERC20(_token).transfer(owner(), _amount);
    }
}