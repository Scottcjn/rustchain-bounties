import path from "node:path";
import dotenv from "dotenv";
import type { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";

// Always load contracts/.env (same folder as this file), regardless of shell cwd
dotenv.config({ path: path.join(__dirname, ".env") });

// ── helpers ─────────────────────────────────────────────────────────────
function getAccounts(): string[] {
  const k = process.env.DEPLOYER_PRIVATE_KEY?.trim();
  if (!k || k === "PASTE_YOUR_PRIVATE_KEY_HERE" || k === "0x...") return [];
  // Accept with or without 0x prefix
  return [k.startsWith("0x") ? k : `0x${k}`];
}

// ── config ──────────────────────────────────────────────────────────────
const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.28",
    settings: { evmVersion: "cancun", optimizer: { enabled: true, runs: 200 } },
  },
  networks: {
    hardhat: {},
    baseSepolia: {
      url: process.env.BASE_SEPOLIA_RPC_URL || "https://sepolia.base.org",
      chainId: 84532,
      accounts: getAccounts(),
    },
    base: {
      url: process.env.BASE_MAINNET_RPC_URL || "https://mainnet.base.org",
      chainId: 8453,
      accounts: getAccounts(),
    },
  },

  // ── Verification ────────────────────────────────────────────────────
  // Per-network object apiKey routes to BaseScan's own API endpoints.
  // Create your key at: https://basescan.org/myapikey (free, instant)
  // hardhat-verify 2.1.x has Base Sepolia + Base built in (see --list-networks).
  etherscan: {
    apiKey: {
      baseSepolia: process.env.BASESCAN_API_KEY?.trim() || "",
      base:        process.env.BASESCAN_API_KEY?.trim() || "",
    },
  },
  sourcify: { enabled: true },
};

export default config;
