# API Documentation

## Overview

RustChain provides comprehensive REST and WebSocket APIs for interacting with the blockchain.

## REST API

### Base URL
```
https://api.rustchain.io/v1
```

### Endpoints

#### Blockchain
- `GET /blocks` - Get all blocks
- `GET /blocks/{hash}` - Get block by hash
- `POST /blocks` - Create new block

#### Transactions
- `GET /transactions` - Get all transactions
- `POST /transactions` - Create new transaction

#### Mining
- `GET /mining/stats` - Get mining statistics
- `POST /mining/start` - Start mining
- `POST /mining/stop` - Stop mining

## WebSocket API

Connect to `wss://api.rustchain.io/v1/ws` for real-time updates.

## Authentication

All API requests require authentication using API keys.

## Rate Limiting

- 100 requests per minute for authenticated users
- 10 requests per minute for unauthenticated users

## Error Handling

API uses standard HTTP status codes and error responses.