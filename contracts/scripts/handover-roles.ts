/**
 * Run after deployment if you did not set MULTISIG_ADDRESS / BRIDGE_MINTER_ADDRESS
 * in the initial deploy, or to fix up roles.
 *
 * Env: DEPLOYER_PRIVATE_KEY, WRTC_ADDRESS, BRIDGE_MINTER_ADDRESS, MULTISIG_ADDRESS
 *
 * Order: grant MINTER to bridge → revoke MINTER from deployer →
 *        grant PAUSER + ADMIN to multisig → revoke PAUSER from deployer →
 *        renounce ADMIN from deployer.
 */
import { ethers } from "hardhat";

async function main() {
  const addr = process.env.WRTC_ADDRESS;
  const bridge = process.env.BRIDGE_MINTER_ADDRESS;
  const multisig = process.env.MULTISIG_ADDRESS;
  if (!addr || !bridge || !multisig) {
    throw new Error("Set WRTC_ADDRESS, BRIDGE_MINTER_ADDRESS, MULTISIG_ADDRESS in .env");
  }

  const [deployer] = await ethers.getSigners();
  if (!deployer) {
    throw new Error("No deployer account — set DEPLOYER_PRIVATE_KEY in contracts/.env");
  }
  const wrtc = await ethers.getContractAt("wRTC", addr);

  const MINTER = await wrtc.MINTER_ROLE();
  const PAUSER = await wrtc.PAUSER_ROLE();
  const ADMIN = await wrtc.DEFAULT_ADMIN_ROLE();

  if (!(await wrtc.hasRole(ADMIN, deployer.address))) {
    throw new Error("Deployer is not DEFAULT_ADMIN — use multisig to run role changes");
  }

  // ── 1. Minter handover ──────────────────────────────────────────────
  await (await wrtc.grantRole(MINTER, bridge)).wait();
  console.log("✅ Granted MINTER_ROLE to", bridge);
  if (await wrtc.hasRole(MINTER, deployer.address)) {
    await (await wrtc.revokeRole(MINTER, deployer.address)).wait();
    console.log("✅ Revoked MINTER_ROLE from deployer");
  }

  // ── 2. Pauser handover ─────────────────────────────────────────────
  await (await wrtc.grantRole(PAUSER, multisig)).wait();
  console.log("✅ Granted PAUSER_ROLE to", multisig);
  if (await wrtc.hasRole(PAUSER, deployer.address)) {
    await (await wrtc.revokeRole(PAUSER, deployer.address)).wait();
    console.log("✅ Revoked PAUSER_ROLE from deployer");
  }

  // ── 3. Admin handover (last — deployer loses everything) ───────────
  await (await wrtc.grantRole(ADMIN, multisig)).wait();
  console.log("✅ Granted DEFAULT_ADMIN_ROLE to", multisig);
  await (await wrtc.renounceRole(ADMIN, deployer.address)).wait();
  console.log("✅ Deployer renounced DEFAULT_ADMIN_ROLE");

  console.log("\n🔒 Handover complete. Deployer holds no roles.");
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
