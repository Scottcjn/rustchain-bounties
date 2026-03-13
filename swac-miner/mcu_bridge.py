#!/usr/bin/env python3
"""
微控制器桥接 - SWAC 与外部 MCU 通信
负责：
- 从网络接收挖矿任务
- 预处理消息块
- 与 SWAC 模拟器通信
- 提交结果
"""

try:
    import serial
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False
    serial = None

import struct
import time
from typing import Optional, List
from swac_simulator import SWACSimulator


class MCUBridge:
    """微控制器桥接类"""
    
    # 协议命令
    CMD_RESET = 0x01
    CMD_LOAD_BLOCK = 0x02
    CMD_START_HASH = 0x03
    CMD_GET_RESULT = 0x04
    CMD_STATUS = 0x05
    
    def __init__(self, port: str = 'COM3', baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.simulator = SWACSimulator()
        self.connected = False
        if not HAS_SERIAL:
            print("注意：pyserial 未安装，使用模拟器模式")
    
    def connect(self) -> bool:
        """连接到微控制器"""
        if not HAS_SERIAL:
            print("  使用软件模拟器模式")
            return False
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1.0
            )
            self.connected = True
            print(f"✓ 已连接到 {self.port}")
            return True
        except Exception as e:
            print(f"✗ 连接失败：{e}")
            print("  使用软件模拟器模式")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connected = False
    
    def _send_command(self, cmd: int, data: bytes = b'') -> bool:
        """发送命令到 MCU"""
        if not self.connected or not self.ser:
            return False
        
        # 帧格式：[START][CMD][LEN][DATA...][CHECKSUM]
        start = 0xAA
        length = len(data)
        checksum = (cmd + length + sum(data)) & 0xFF
        
        frame = bytes([start, cmd, length]) + data + bytes([checksum])
        self.ser.write(frame)
        return True
    
    def _read_response(self, timeout: float = 1.0) -> Optional[bytes]:
        """从 MCU 读取响应"""
        if not self.ser:
            return None
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.ser.in_waiting >= 2:
                start = self.ser.read(1)
                if start == b'\xAA':
                    cmd = self.ser.read(1)[0]
                    length = self.ser.read(1)[0]
                    if self.ser.in_waiting >= length + 1:
                        data = self.ser.read(length)
                        checksum = self.ser.read(1)[0]
                        
                        # 验证校验和
                        expected_cs = (cmd + length + sum(data)) & 0xFF
                        if checksum == expected_cs:
                            return data
        return None
    
    def reset(self) -> bool:
        """重置 SWAC"""
        if self.connected:
            return self._send_command(self.CMD_RESET)
        else:
            # 模拟器模式
            self.simulator = SWACSimulator()
            return True
    
    def load_message_block(self, block: bytes) -> bool:
        """加载 512 位消息块"""
        if len(block) != 64:
            print(f"✗ 消息块长度错误：{len(block)} (应为 64)")
            return False
        
        if self.connected:
            return self._send_command(self.CMD_LOAD_BLOCK, block)
        else:
            # 模拟器模式：直接加载到 SWAC 内存
            # 将 64 字节拆分为 37 位字
            words = []
            for i in range(0, 64, 4):
                if i + 4 <= 64:
                    word = int.from_bytes(block[i:i+4], 'big')
                    words.append(word)
            
            # 加载到消息调度区 (地址 80-143)
            self.simulator.load_data(words[:16], 80)
            # 扩展 W[16..63] 在 SWAC 中计算
            return True
    
    def start_hash(self) -> bool:
        """开始哈希计算"""
        if self.connected:
            return self._send_command(self.CMD_START_HASH)
        else:
            # 模拟器模式：运行 SWAC 程序
            # 这里简化处理，实际应加载并运行汇编程序
            self.simulator.run(max_cycles=10000)
            return True
    
    def get_result(self) -> Optional[List[int]]:
        """获取哈希结果"""
        if self.connected:
            self._send_command(self.CMD_GET_RESULT)
            data = self._read_response()
            if data and len(data) == 32:
                # 解析 8 个 32 位哈希值
                result = []
                for i in range(8):
                    h = int.from_bytes(data[i*4:(i+1)*4], 'big')
                    result.append(h)
                return result
            return None
        else:
            # 模拟器模式
            return self.simulator.get_hash_state()
    
    def get_status(self) -> dict:
        """获取状态"""
        if self.connected:
            self._send_command(self.CMD_STATUS)
            data = self._read_response()
            if data:
                return {
                    'connected': True,
                    'status': data[0],
                    'cycle_count': int.from_bytes(data[1:4], 'big'),
                }
        return {
            'connected': False,
            'simulator': True,
            'cycles': self.simulator.cycles,
        }


class MiningTask:
    """挖矿任务"""
    
    def __init__(self, task_id: str, target: bytes, nonce_start: int = 0):
        self.task_id = task_id
        self.target = target  # 目标难度
        self.nonce_start = nonce_start
        self.nonce_current = nonce_start
    
    def next_block(self, header: bytes) -> bytes:
        """生成下一个消息块 (带递增 nonce)"""
        # header 结构：[version][prev_hash][merkle_root][timestamp][bits][nonce]
        # 80 字节区块头 + 填充到 512 位
        
        block = bytearray(header)
        # 更新 nonce (4 字节，小端)
        nonce_bytes = self.nonce_current.to_bytes(4, 'little')
        block[76:80] = nonce_bytes
        self.nonce_current += 1
        
        # 填充到 64 字节 (512 位)
        # 实际 SHA256D 需要两次哈希，这里简化
        while len(block) < 64:
            block.append(0x80 if len(block) == 64 else 0x00)
        
        return bytes(block[:64])


def mine_block(bridge: MCUBridge, task: MiningTask, header: bytes, 
               max_attempts: int = 1000) -> Optional[dict]:
    """
    挖矿主循环
    返回找到的有效 nonce 或 None
    """
    print(f"\n🔨 开始挖矿任务：{task.task_id}")
    print(f"   目标：{task.target.hex()[:16]}...")
    print(f"   起始 nonce: {task.nonce_start}")
    
    for i in range(max_attempts):
        if i % 100 == 0:
            status = bridge.get_status()
            print(f"   进度：{i}/{max_attempts} (cycles: {status.get('cycles', 'N/A')})")
        
        # 生成消息块
        block = task.next_block(header)
        
        # 加载并计算
        if not bridge.load_message_block(block):
            print("✗ 加载消息块失败")
            continue
        
        if not bridge.start_hash():
            print("✗ 启动哈希失败")
            continue
        
        # 获取结果
        result = bridge.get_result()
        if result:
            # 将哈希值转换为字节
            hash_bytes = b''.join(h.to_bytes(4, 'big') for h in result)
            
            # 检查是否满足难度目标
            if hash_bytes < task.target:
                print(f"\n✅ 找到有效 nonce!")
                print(f"   Nonce: {task.nonce_current - 1}")
                print(f"   Hash: {hash_bytes.hex()}")
                return {
                    'task_id': task.task_id,
                    'nonce': task.nonce_current - 1,
                    'hash': hash_bytes.hex(),
                    'header': header.hex(),
                }
    
    print(f"\n⏱️ 未找到有效 nonce (尝试 {max_attempts} 次)")
    return None


if __name__ == '__main__':
    # 测试桥接
    print("=" * 50)
    print("SWAC Miner - MCU Bridge")
    print("=" * 50)
    
    bridge = MCUBridge(port='COM3')
    
    if not bridge.connect():
        print("\n使用模拟器模式...")
    
    # 创建测试任务
    task = MiningTask(
        task_id="test-001",
        target=b'\x00' * 4 + b'\xff' * 28,  # 简单难度
        nonce_start=0
    )
    
    # 测试区块头 (80 字节，简化)
    test_header = bytes([0x01, 0x00, 0x00, 0x00])  # version
    test_header += bytes([0x00] * 32)  # prev_hash
    test_header += bytes([0x00] * 32)  # merkle_root
    test_header += bytes([0x00] * 4)   # timestamp
    test_header += bytes([0x00] * 4)   # bits
    test_header += bytes([0x00] * 4)   # nonce (会被覆盖)
    
    # 运行挖矿
    result = mine_block(bridge, task, test_header, max_attempts=100)
    
    if result:
        print(f"\n🎉 挖矿成功!")
        print(f"   钱包：RTC4325af95d26d59c3ef025963656d22af638bb96b")
    
    bridge.disconnect()
