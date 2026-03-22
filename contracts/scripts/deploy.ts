/**
 * Deploy wRTC on Base / Base Sepolia.
 *
 * Env:
 *   DEPLOYER_PRIVATE_KEY  — deployer EOA (0x + 64 hex)
 *   MULTISIG_ADDRESS      — optional; receives DEFAULT_ADMIN_ROLE (deployer revoked)
 *   BRIDGE_MINTER_ADDRESS — optional; receives MINTER_ROLE
 *   ETHERSCAN_API_KEY     — optional; enables automatic post-deploy verification
 *
 * After deploy: confirm roles on BaseScan, ensure deployer holds no roles
 * if multisig + bridge minter were set.
 */
import { ethers, run, network } from "hardhat";
import * as fs from "node:fs";
import * as path from "node:path";

async function main() {
  const [deployer] = await ethers.getSigners();
  if (!deployer) {
    throw new Error(
      "No deployer account. Set DEPLOYER_PRIVATE_KEY in contracts/.env " +
      "(0x + 64 hex, no quotes). Run npm install in contracts/ first."
    );
  }

  const chainId = Number((await ethers.provider.getNetwork()).chainId);
  const networkName = network.name;
  const multisig = process.env.MULTISIG_ADDRESS?.trim();
  const bridgeMinter = process.env.BRIDGE_MINTER_ADDRESS?.trim();

  console.log("┌────────────────────────────────────────────");
  console.log(`│ Network:  ${networkName} (chainId ${chainId})`);
  console.log(`│ Deployer: ${deployer.address}`);
  console.log("└────────────────────────────────────────────");

  // ── Deploy ──────────────────────────────────────────────────────────
  const WRTC = await ethers.getContractFactory("wRTC");
  const wrtc = await WRTC.deploy(deployer.address);
  await wrtc.waitForDeployment();
  const addr = await wrtc.getAddress();
  const deployTx = wrtc.deploymentTransaction()?.hash;

  console.log(`\n  ✅ wRTC deployed: ${addr}`);
  console.log(`  📝 Deploy tx:    ${deployTx}`);

  // ── Role handover (optional, at deploy time) ────────────────────────
  const minterAddr = bridgeMinter || deployer.address;
  if (minterAddr.toLowerCase() !== deployer.address.toLowerCase()) {
    await (await wrtc.grantRole(await wrtc.MINTER_ROLE(), minterAddr)).wait();
    await (await wrtc.revokeRole(await wrtc.MINTER_ROLE(), deployer.address)).wait();
    console.log(`  🔑 MINTER_ROLE → ${minterAddr}`);
  }

  if (multisig && multisig.toLowerCase() !== deployer.address.toLowerCase()) {
    // Transfer admin
    await (await wrtc.grantRole(await wrtc.DEFAULT_ADMIN_ROLE(), multisig)).wait();
    // Transfer pauser to multisig too
    await (await wrtc.grantRole(await wrtc.PAUSER_ROLE(), multisig)).wait();
    await (await wrtc.revokeRole(await wrtc.PAUSER_ROLE(), deployer.address)).wait();
    // Renounce admin last (deployer loses all privilege)
    await (await wrtc.renounceRole(await wrtc.DEFAULT_ADMIN_ROLE(), deployer.address)).wait();
    console.log(`  🔑 DEFAULT_ADMIN_ROLE → ${multisig} (deployer renounced)`);
    console.log(`  🔑 PAUSER_ROLE → ${multisig}`);
  }

  // ── Save deployment artifact ────────────────────────────────────────
  const artifact = {
    network: networkName,
    chainId,
    contract: addr,
    deployTx,
    deployer: deployer.address,
    minter: minterAddr,
    multisig: multisig || deployer.address,
    timestamp: new Date().toISOString(),
    constructorArgs: [deployer.address],
  };

  const deploymentsDir = path.join(__dirname, "..", "deployments");
  if (!fs.existsSync(deploymentsDir)) fs.mkdirSync(deploymentsDir, { recursive: true });
  const artifactPath = path.join(deploymentsDir, `${networkName}-${Date.now()}.json`);
  fs.writeFileSync(artifactPath, JSON.stringify(artifact, null, 2));
  console.log(`  💾 Artifact:     ${artifactPath}`);

  // ── Auto-verify (best effort) ──────────────────────────────────────
  if (process.env.ETHERSCAN_API_KEY?.trim()) {
    console.log("\n  ⏳ Waiting 15s for block explorer indexing...");
    await new Promise((r) => setTimeout(r, 15_000));
    try {
      await run("verify:verify", {
        address: addr,
        constructorArguments: [deployer.address],
      });
      console.log("  ✅ Verified on block explorer");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      if (msg.includes("Already Verified") || msg.includes("already verified")) {
        console.log("  ✅ Already verified");
      } else {
        console.warn("  ⚠️  Auto-verify failed (verify manually):", msg);
        console.log(`  Manual: npx hardhat verify --network ${networkName} ${addr} "${deployer.address}"`);
      }
    }
  } else {
    console.log("\n  ℹ️  No ETHERSCAN_API_KEY — skipping auto-verify");
    console.log(`  Manual: npx hardhat verify --network ${networkName} ${addr} "${deployer.address}"`);
  }

  // ── Explorer link ───────────────────────────────────────────────────
  const explorer = chainId === 84532
    ? `https://sepolia.basescan.org/address/${addr}`
    : `https://basescan.org/address/${addr}`;
  console.log(`\n  🔗 Explorer: ${explorer}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
