# RustChain API Documentation

## Overview

This document provides information about the RustChain Node API endpoints and their usage. The API is documented using OpenAPI 3.0 specification and can be viewed interactively using Swagger UI.

## Interactive Documentation

You can view the interactive API documentation at:

- [Swagger UI](swagger-ui.html)
- [OpenAPI YAML Specification](openapi.yaml)

## API Endpoints

### Nodes

- `GET /nodes` - List all nodes in the network
- `GET /nodes/{nodeId}` - Get details for a specific node

### Miners

- `GET /miners` - List all miners in the network

### Bounties

- `GET /bounties` - List all available bounties
- `GET /bounties/{bountyId}` - Get details for a specific bounty

## Authentication

The API uses API key authentication. Include your API key in the `X-API-Key` header for all requests.

## Error Responses

All endpoints return appropriate HTTP status codes:

- `200` - Success
- `404` - Resource not found
- `500` - Internal server error

## Rate Limiting

The API implements rate limiting to ensure fair usage. Please refer to the specific endpoint documentation for rate limits.

## Getting Started

1. Obtain an API key from the RustChain dashboard
2. Use the Swagger UI to explore the API endpoints
3. Make API requests using your preferred HTTP client

## Support

For API-related questions or issues, please contact:

- Email: api-support@rustchain.com
- Discord: RustChain API Support Channel

## Changelog

### v1.0.0
- Initial API release
- Basic node, miner, and bounty endpoints
- OpenAPI 3.0 specification
- Swagger UI integration