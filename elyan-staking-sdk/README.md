# @elyan/staking SDK

A TypeScript client for the Elyan staking protocol.

## Usage

```typescript
import { StakingClient } from './index';

const client = new StakingClient(
  'your-api-key',
  'gate-public-key-hex'
);

// Stake
const result = await client.stake(100, 'your-wallet-address');

// Verify a verdict
const isValid = await client.verify(verdict);
