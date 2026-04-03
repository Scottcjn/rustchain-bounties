import { shouldCopy, PolicyConfig, FollowerState, DEFAULT_POLICY } from "../policy";
import { Trade } from "../types";

function makeTrade(amount: number): Trade {
  return {
    signature: "test-sig",
    from: "SourcePubkey111111111111111111111111111111111",
    to: "DestPubkey1111111111111111111111111111111111",
    amount,
  };
}

describe("shouldCopy policy checks", () => {
  const policy: PolicyConfig = {
    minTradeLamports: 1_000_000,
    maxPerWalletLamports: 100_000_000,
    slippagePct: 2,
  };

  it("allows a trade within limits", () => {
    const state: FollowerState = { totalSpentLamports: 0 };
    const result = shouldCopy(makeTrade(5_000_000), state, policy);
    expect(result.allowed).toBe(true);
    expect(result.reason).toBeUndefined();
  });

  it("blocks trade below minimum", () => {
    const state: FollowerState = { totalSpentLamports: 0 };
    const result = shouldCopy(makeTrade(500_000), state, policy);
    expect(result.allowed).toBe(false);
    expect(result.reason).toContain("below minimum");
  });

  it("blocks trade that would exceed per-wallet cap", () => {
    const state: FollowerState = { totalSpentLamports: 95_000_000 };
    const result = shouldCopy(makeTrade(10_000_000), state, policy);
    expect(result.allowed).toBe(false);
    expect(result.reason).toContain("exceed per-wallet cap");
  });

  it("allows trade right at the cap boundary", () => {
    const state: FollowerState = { totalSpentLamports: 90_000_000 };
    const result = shouldCopy(makeTrade(10_000_000), state, policy);
    expect(result.allowed).toBe(true);
  });

  it("uses DEFAULT_POLICY when no config provided", () => {
    const state: FollowerState = { totalSpentLamports: 0 };
    const result = shouldCopy(makeTrade(DEFAULT_POLICY.minTradeLamports), state);
    expect(result.allowed).toBe(true);
  });

  it("blocks when exactly at zero amount below minimum", () => {
    const state: FollowerState = { totalSpentLamports: 0 };
    const result = shouldCopy(makeTrade(999_999), state, policy);
    expect(result.allowed).toBe(false);
  });
});
