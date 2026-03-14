#!/usr/bin/env python3
"""
RustChain Discord Bot - Query RustChain blockchain data from Discord
"""

import os
import discord
from discord.ext import commands
import requests

# Configuration
RPC_URL = os.getenv("RUSTCHAIN_RPC_URL", "https://rpc.rustchain.com")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


def rpc_call(method, params):
    """Make JSON-RPC call to RustChain"""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    try:
        response = requests.post(RPC_URL, json=payload, timeout=10)
        response.raise_for_status()
        return response.json().get("result")
    except Exception as e:
        return {"error": str(e)}


@bot.event
async def on_ready():
    print(f"{bot.user} is ready!")


@bot.command(help="Get account balance")
async def balance(ctx, address: str):
    """Query RTC balance for an address"""
    result = rpc_call("eth_getBalance", [address, "latest"])
    if result and "error" not in str(result):
        balance_rtc = int(result, 16) / 1e18 if result != "0x0" else 0
        await ctx.send(f"💰 Balance for `{address}`:\n**{balance_rtc:.4f} RTC**")
    else:
        await ctx.send(f"❌ Error: {result}")


@bot.command(help="Get latest block number")
async def block(ctx):
    """Get latest block number"""
    result = rpc_call("eth_blockNumber", [])
    if result:
        block_num = int(result, 16)
        await ctx.send(f"📦 Latest block: **#{block_num}**")
    else:
        await ctx.send("❌ Error getting block number")


@bot.command(help="Get transaction by hash")
async def tx(ctx, tx_hash: str):
    """Query transaction details"""
    result = rpc_call("eth_getTransactionByHash", [tx_hash])
    if result and "error" not in str(result):
        await ctx.send(f"✅ Transaction found:\nFrom: `{result.get('from')}`\nTo: `{result.get('to')}`\nValue: `{result.get('value')}`")
    else:
        await ctx.send("❌ Transaction not found")


@bot.command(help="Get network stats")
async def stats(ctx):
    """Get network statistics"""
    block_result = rpc_call("eth_blockNumber", [])
    chain_result = rpc_call("eth_chainId", [])
    
    if block_result and chain_result:
        block_num = int(block_result, 16)
        chain_id = int(chain_result, 16)
        await ctx.send(f"📊 **RustChain Stats**\nChain ID: `{chain_id}`\nLatest Block: **#{block_num}**")
    else:
        await ctx.send("❌ Error getting stats")


if __name__ == "__main__":
    if DISCORD_TOKEN:
        bot.run(DISCORD_TOKEN)
    else:
        print("Please set DISCORD_TOKEN environment variable")
