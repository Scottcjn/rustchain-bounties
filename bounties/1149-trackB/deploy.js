/**
 * wRTC ERC-20 Deployment Script for Base
 * 
 * Track B: Base ERC-20 Token (75 RTC Bounty)
 * 
 * Usage:
 *   npx hardhat run scripts/deploy.js --network base
 *   npx hardhat run scripts/deploy.js --network baseSepolia
 * 
 * Requirements:
 *   - Base RPC URL configured in hardhat.config.js
 *   - Private key with ETH for gas
 *   - OpenZeppelin Contracts installed: npm install @openzeppelin/contracts
 */

const hre = require("hardhat");

async function main() {
    console.log("🚀 Deploying wRTC ERC-20 on Base...");
    console.log("Network:", hre.network.name);
    
    // Get deployer account
    const [deployer] = await hre.ethers.getSigners();
    console.log("📤 Deploying with account:", deployer.address);
    
    // Check balance
    const balance = await hre.ethers.provider.getBalance(deployer.address);
    console.log("💰 Account balance:", hre.ethers.formatEther(balance), "ETH");
    
    // Deploy wRTC contract
    const WRTC = await hre.ethers.getContractFactory("wRTC");
    const wrtc = await WRTC.deploy();
    await wrtc.waitForDeployment();
    
    const contractAddress = await wrtc.getAddress();
    console.log("✅ wRTC deployed to:", contractAddress);
    
    // Verify deployment
    const name = await wrtc.name();
    const symbol = await wrtc.symbol();
    const decimals = await wrtc.decimals();
    const totalSupply = await wrtc.totalSupply();
    const owner = await wrtc.owner();
    
    console.log("\n📊 Contract Details:");
    console.log("  Name:", name);
    console.log("  Symbol:", symbol);
    console.log("  Decimals:", decimals);
    console.log("  Total Supply:", hre.ethers.formatUnits(totalSupply, decimals), "wRTC");
    console.log("  Owner:", owner);
    
    // Verification instructions
    console.log("\n🔍 To verify on BaseScan:");
    console.log(`  npx hardhat verify --network ${hre.network.name} ${contractAddress}`);
    
    console.log("\n📝 Next Steps:");
    console.log("  1. Verify contract on BaseScan");
    console.log("  2. Add token to MetaMask");
    console.log("  3. Transfer ownership to bridge contract");
    console.log("  4. Update bounty PR with deployment details");
    
    return {
        contractAddress,
        name,
        symbol,
        decimals,
        deployer: deployer.address
    };
}

// Handle deployment
main()
    .then((result) => {
        console.log("\n✅ Deployment complete!");
        process.exit(0);
    })
    .catch((error) => {
        console.error("❌ Deployment failed:", error);
        process.exit(1);
    });
