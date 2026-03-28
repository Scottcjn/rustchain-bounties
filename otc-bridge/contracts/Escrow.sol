// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title RustChain OTC Bridge Escrow Contract
 * @dev ETH/ERC20 escrow for atomic swaps with RTC
 */
contract OTCEscrow {
    enum State { Created, Funded, Completed, Cancelled }
    
    struct Trade {
        address buyer;
        address seller;
        address asset;  // address(0) for ETH
        uint256 cryptoAmount;
        uint256 rtcAmount;
        uint256 pricePerRTC;
        State state;
        bytes32 rtcTxHash;
    }
    
    mapping(bytes32 => Trade) public trades;
    mapping(address => uint256) public balances;
    
    event TradeCreated(bytes32 indexed tradeId, address buyer, address seller);
    event TradeFunded(bytes32 indexed tradeId);
    event TradeCompleted(bytes32 indexed tradeId);
    event TradeCancelled(bytes32 indexed tradeId);
    
    /**
     * @dev Create a new trade
     */
    function createTrade(
        bytes32 tradeId,
        address seller,
        address asset,
        uint256 cryptoAmount,
        uint256 rtcAmount,
        uint256 pricePerRTC
    ) external payable {
        require(trades[tradeId].state == State.Created, "Trade exists");
        
        trades[tradeId] = Trade({
            buyer: msg.sender,
            seller: seller,
            asset: asset,
            cryptoAmount: cryptoAmount,
            rtcAmount: rtcAmount,
            pricePerRTC: pricePerRTC,
            state: State.Created,
            rtcTxHash: bytes32(0)
        });
        
        emit TradeCreated(tradeId, msg.sender, seller);
    }
    
    /**
     * @dev Fund the trade (deposit crypto)
     */
    function fundTrade(bytes32 tradeId) external payable {
        Trade storage trade = trades[tradeId];
        require(trade.state == State.Created, "Invalid state");
        require(msg.value >= trade.cryptoAmount, "Insufficient deposit");
        
        trade.state = State.Funded;
        emit TradeFunded(tradeId);
    }
    
    /**
     * @dev Complete trade - called after RTC side confirmed
     */
    function completeTrade(bytes32 tradeId, bytes32 rtcTxHash) external {
        Trade storage trade = trades[tradeId];
        require(trade.state == State.Funded, "Not funded");
        
        trade.rtcTxHash = rtcTxHash;
        trade.state = State.Completed;
        
        // Release crypto to seller
        payable(trade.seller).transfer(trade.cryptoAmount);
        
        emit TradeCompleted(tradeId);
    }
    
    /**
     * @dev Cancel trade and refund
     */
    function cancelTrade(bytes32 tradeId) external {
        Trade storage trade = trades[tradeId];
        require(trade.state == State.Created, "Cannot cancel");
        
        trade.state = State.Cancelled;
        payable(trade.buyer).transfer(trade.cryptoAmount);
        
        emit TradeCancelled(tradeId);
    }
    
    /**
     * @dev Get trade details
     */
    function getTrade(bytes32 tradeId) external view returns (
        address buyer,
        address seller,
        uint256 cryptoAmount,
        uint256 rtcAmount,
        string memory state
    ) {
        Trade storage trade = trades[tradeId];
        return (
            trade.buyer,
            trade.seller,
            trade.cryptoAmount,
            trade.rtcAmount,
            stateToString(trade.state)
        );
    }
    
    function stateToString(State s) internal pure returns (string memory) {
        if (s == State.Created) return "Created";
        if (s == State.Funded) return "Funded";
        if (s == State.Completed) return "Completed";
        return "Cancelled";
    }
}