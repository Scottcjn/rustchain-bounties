#!/usr/bin/env python3
"""
网络桥接 - SWAC Miner 网络连接层
负责：
- 连接矿池/网络
- 获取挖矿任务
- 提交挖矿结果
- 心跳保活
"""

import socket
import json
import time
import hashlib
from typing import Optional, Dict, Any
from dataclasses import dataclass
from mcu_bridge import MCUBridge, MiningTask, mine_block


@dataclass
class PoolConfig:
    """矿池配置"""
    host: str
    port: int
    worker_name: str
    password: str = "x"
    wallet: str = "RTC4325af95d26d59c3ef025963656d22af638bb96b"


class NetworkBridge:
    """网络桥接类"""
    
    def __init__(self, config: PoolConfig):
        self.config = config
        self.sock: Optional[socket.socket] = None
        self.connected = False
        self.last_heartbeat = 0
    
    def connect(self) -> bool:
        """连接到矿池"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10.0)
            self.sock.connect((self.config.host, self.config.port))
            self.connected = True
            
            # 发送订阅消息
            self._send({
                "id": 1,
                "method": "mining.subscribe",
                "params": []
            })
            
            # 等待响应
            response = self._recv()
            if response:
                print(f"✓ 已连接到矿池 {self.config.host}:{self.config.port}")
                return True
            
            return False
        except Exception as e:
            print(f"✗ 连接失败：{e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.sock:
            self.sock.close()
        self.connected = False
    
    def _send(self, message: Dict[str, Any]) -> bool:
        """发送 JSON-RPC 消息"""
        if not self.sock:
            return False
        
        try:
            data = json.dumps(message) + "\n"
            self.sock.sendall(data.encode('utf-8'))
            return True
        except Exception as e:
            print(f"✗ 发送失败：{e}")
            return False
    
    def _recv(self, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
        """接收 JSON-RPC 消息"""
        if not self.sock:
            return None
        
        try:
            self.sock.settimeout(timeout)
            data = b''
            while True:
                chunk = self.sock.recv(1)
                if not chunk:
                    break
                if chunk == b'\n':
                    break
                data += chunk
            
            if data:
                return json.loads(data.decode('utf-8'))
            return None
        except socket.timeout:
            return None
        except Exception as e:
            print(f"✗ 接收失败：{e}")
            return None
    
    def authorize(self) -> bool:
        """授权 worker"""
        return self._send({
            "id": 2,
            "method": "mining.authorize",
            "params": [
                f"{self.config.wallet}.{self.config.worker_name}",
                self.config.password
            ]
        })
    
    def get_job(self) -> Optional[Dict[str, Any]]:
        """获取挖矿任务"""
        # 等待矿池推送任务
        while True:
            msg = self._recv(timeout=30.0)
            if msg:
                if msg.get("method") == "mining.notify":
                    params = msg.get("params", [])
                    if len(params) >= 8:
                        return {
                            "job_id": params[0],
                            "prev_hash": params[1],
                            "coinb1": params[2],
                            "coinb2": params[3],
                            "merkle_branch": params[4],
                            "version": params[5],
                            "nbits": params[6],
                            "ntime": params[7],
                            "clean_jobs": params[8] if len(params) > 8 else False
                        }
                elif msg.get("id") == 2:
                    # 授权响应
                    if msg.get("result"):
                        print("✓ 授权成功")
                    continue
            return None
    
    def submit_share(self, job_id: str, nonce: int, header_hash: str) -> bool:
        """提交挖矿结果"""
        return self._send({
            "id": 3,
            "method": "mining.submit",
            "params": [
                f"{self.config.wallet}.{self.config.worker_name}",
                job_id,
                f"{nonce:08x}",
                header_hash
            ]
        })
    
    def send_heartbeat(self) -> bool:
        """发送心跳"""
        now = time.time()
        if now - self.last_heartbeat < 60:
            return True
        
        self.last_heartbeat = now
        return self._send({
            "id": 999,
            "method": "mining.keepalived",
            "params": []
        })


def build_block_header(job: Dict[str, Any], nonce: int) -> bytes:
    """构建区块头"""
    # 简化实现，实际需要根据具体币种协议
    header = bytearray()
    
    # version (4 bytes, little-endian)
    version = int(job.get("version", "1"), 16)
    header.extend(version.to_bytes(4, 'little'))
    
    # prev_hash (32 bytes)
    prev_hash = bytes.fromhex(job["prev_hash"])
    header.extend(prev_hash)
    
    # merkle_root (32 bytes) - 需要从 coinbase 和 merkle_branch 计算
    # 这里简化处理
    merkle_root = hashlib.sha256(hashlib.sha256(
        bytes.fromhex(job["coinb1"]) + 
        bytes.fromhex(job["coinb2"])
    ).digest()).digest()
    header.extend(merkle_root)
    
    # timestamp (4 bytes)
    ntime = int(job["ntime"], 16)
    header.extend(ntime.to_bytes(4, 'little'))
    
    # nbits (4 bytes)
    nbits = int(job["nbits"], 16)
    header.extend(nbits.to_bytes(4, 'little'))
    
    # nonce (4 bytes)
    header.extend(nonce.to_bytes(4, 'little'))
    
    return bytes(header)


def calculate_target(nbits: str) -> bytes:
    """从 nbits 计算目标难度"""
    nbits_int = int(nbits, 16)
    exponent = nbits_int >> 24
    mantissa = nbits_int & 0xFFFFFF
    
    target = mantissa * (256 ** (exponent - 3))
    target_bytes = target.to_bytes(32, 'big')
    return target_bytes


def run_miner(pool_config: PoolConfig, bridge: MCUBridge):
    """运行挖矿主循环"""
    print("=" * 60)
    print("SWAC Miner - Network Bridge")
    print("=" * 60)
    print(f"钱包地址：{pool_config.wallet}")
    print(f"矿池：{pool_config.host}:{pool_config.port}")
    print(f"Worker: {pool_config.worker_name}")
    print("=" * 60)
    
    # 连接矿池
    if not network.connect():
        print("✗ 无法连接到矿池，退出")
        return
    
    # 授权
    if not network.authorize():
        print("✗ 授权失败，退出")
        return
    
    print("\n🚀 开始挖矿...\n")
    
    accepted = 0
    rejected = 0
    total_hashes = 0
    
    try:
        while True:
            # 获取新任务
            print("⏳ 等待新任务...")
            job = network.get_job()
            if not job:
                print("✗ 获取任务失败")
                time.sleep(5)
                continue
            
            print(f"\n📋 新任务:")
            print(f"   Job ID: {job['job_id']}")
            print(f"   难度：{job['nbits']}")
            
            # 计算目标
            target = calculate_target(job['nbits'])
            
            # 创建挖矿任务
            task = MiningTask(
                task_id=job['job_id'],
                target=target,
                nonce_start=0
            )
            
            # 构建区块头模板
            header_template = build_block_header(job, 0)
            
            # 执行挖矿
            result = mine_block(bridge, task, header_template, max_attempts=1000)
            
            if result:
                # 提交结果
                print(f"\n📤 提交结果...")
                if network.submit_share(
                    job['job_id'],
                    result['nonce'],
                    result['hash']
                ):
                    accepted += 1
                    print(f"✅ 接受! (总数：{accepted})")
                else:
                    rejected += 1
                    print(f"❌ 拒绝! (总数：{rejected})")
            
            total_hashes += 1000
            
            # 发送心跳
            network.send_heartbeat()
            
            # 显示统计
            print(f"\n📊 统计:")
            print(f"   接受：{accepted}")
            print(f"   拒绝：{rejected}")
            print(f"   总算力：{total_hashes} hashes")
            
    except KeyboardInterrupt:
        print("\n\n⛔ 用户中断")
    finally:
        network.disconnect()
        bridge.disconnect()
        
        print("\n" + "=" * 60)
        print("挖矿结束")
        print(f"钱包：{pool_config.wallet}")
        print(f"接受：{accepted}")
        print(f"拒绝：{rejected}")
        print("=" * 60)


if __name__ == '__main__':
    # 配置矿池 (示例，需要替换为实际矿池)
    config = PoolConfig(
        host="pool.example.com",  # 替换为实际矿池
        port=3333,
        worker_name="swac-miner-001",
        wallet="RTC4325af95d26d59c3ef025963656d22af638bb96b"
    )
    
    # 创建桥接
    bridge = MCUBridge(port='COM3')
    if not bridge.connect():
        print("使用模拟器模式")
    
    # 创建网络桥接
    network = NetworkBridge(config)
    
    # 运行挖矿
    run_miner(config, bridge)
