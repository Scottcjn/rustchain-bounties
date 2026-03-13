#!/usr/bin/env python3
"""
Paper Tape Communication Protocol

Defines the protocol for communication between AVIDAC and the network bridge.

Protocol Design:
- Simple message framing with STX/ETX
- Fixed-length fields for reliability
- Error detection via checksums
- Optimized for 40-bit word size

This protocol enables the 1953-era AVIDAC architecture to communicate
with modern blockchain networks through a translation layer.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class MiningJob:
    """Represents a mining job sent to AVIDAC."""
    job_id: int           # 32-bit job identifier
    block_header: bytes   # 256-bit block header
    target: bytes         # 256-bit target threshold
    timestamp: int        # 64-bit timestamp


@dataclass
class Solution:
    """Represents a solution found by AVIDAC."""
    job_id: int           # 32-bit job identifier
    nonce: int            # 64-bit nonce solution
    hash_result: bytes    # 256-bit hash result


class PaperTapeProtocol:
    """
    Implements the paper tape communication protocol.
    
    Message Formats:
    
    1. MINING_JOB (Bridge → AVIDAC):
       [STX][JOB_ID_3]...[JOB_ID_0]
       [HEADER_31]...[HEADER_0]
       [TARGET_31]...[TARGET_0]
       [TIMESTAMP_7]...[TIMESTAMP_0][ETX]
       Total: 74 bytes
    
    2. SOLUTION (AVIDAC → Bridge):
       [STX][JOB_ID_3]...[JOB_ID_0]
       [NONCE_7]...[NONCE_0]
       [HASH_31]...[HASH_0][ETX]
       Total: 46 bytes
    
    3. STATUS_REQUEST (Bridge → AVIDAC):
       [STX][0x53][0x54][0x41][0x54][ETX]
       ("STAT" command)
       Total: 7 bytes
    
    4. STATUS_RESPONSE (AVIDAC → Bridge):
       [STX][HASHES_7]...[HASHES_0]
       [ERRORS_2]...[ERRORS_0][ETX]
       Total: 13 bytes
    """
    
    # Control characters
    STX = 0x02  # Start of transmission
    ETX = 0x03  # End of transmission
    ACK = 0x06  # Acknowledge
    NAK = 0x15  # Negative acknowledge
    
    # Message types
    MSG_MINING_JOB = 0x01
    MSG_SOLUTION = 0x02
    MSG_STATUS_REQUEST = 0x03
    MSG_STATUS_RESPONSE = 0x04
    
    def __init__(self):
        """Initialize protocol handler."""
        self.message_count = 0
        self.error_count = 0
    
    def encode_mining_job(self, job: MiningJob) -> List[int]:
        """
        Encode mining job for transmission to AVIDAC.
        
        Args:
            job: MiningJob object
            
        Returns:
            List of bytes (message payload, excludes STX/ETX)
        """
        message = []
        
        # Job ID (4 bytes, big-endian)
        for i in range(3, -1, -1):
            message.append((job.job_id >> (i * 8)) & 0xFF)
        
        # Block header (32 bytes)
        message.extend(job.block_header)
        
        # Target (32 bytes)
        message.extend(job.target)
        
        # Timestamp (8 bytes, big-endian)
        for i in range(7, -1, -1):
            message.append((job.timestamp >> (i * 8)) & 0xFF)
        
        return message
    
    def decode_mining_job(self, data: List[int]) -> Optional[MiningJob]:
        """
        Decode mining job from received data.
        
        Args:
            data: List of bytes (74 bytes expected)
            
        Returns:
            MiningJob object or None if invalid
        """
        if len(data) != 74:
            self.error_count += 1
            return None
        
        try:
            # Parse job ID (4 bytes)
            job_id = 0
            for i in range(4):
                job_id = (job_id << 8) | data[i]
            
            # Parse block header (32 bytes)
            header = bytes(data[4:36])
            
            # Parse target (32 bytes)
            target = bytes(data[36:68])
            
            # Parse timestamp (8 bytes)
            timestamp = 0
            for i in range(68, 76):
                timestamp = (timestamp << 8) | data[i]
            
            return MiningJob(
                job_id=job_id,
                block_header=header,
                target=target,
                timestamp=timestamp
            )
            
        except Exception as e:
            self.error_count += 1
            return None
    
    def encode_solution(self, solution: Solution) -> List[int]:
        """
        Encode solution for transmission to bridge.
        
        Args:
            solution: Solution object
            
        Returns:
            List of bytes (message payload)
        """
        message = []
        
        # Job ID (4 bytes, big-endian)
        for i in range(3, -1, -1):
            message.append((solution.job_id >> (i * 8)) & 0xFF)
        
        # Nonce (8 bytes, big-endian)
        for i in range(7, -1, -1):
            message.append((solution.nonce >> (i * 8)) & 0xFF)
        
        # Hash result (32 bytes)
        message.extend(solution.hash_result)
        
        return message
    
    def decode_solution(self, data: List[int]) -> Optional[Solution]:
        """
        Decode solution from received data.
        
        Args:
            data: List of bytes (44 bytes expected)
            
        Returns:
            Solution object or None if invalid
        """
        if len(data) != 44:
            self.error_count += 1
            return None
        
        try:
            # Parse job ID (4 bytes)
            job_id = 0
            for i in range(4):
                job_id = (job_id << 8) | data[i]
            
            # Parse nonce (8 bytes)
            nonce = 0
            for i in range(4, 12):
                nonce = (nonce << 8) | data[i]
            
            # Parse hash result (32 bytes)
            hash_result = bytes(data[12:44])
            
            return Solution(
                job_id=job_id,
                nonce=nonce,
                hash_result=hash_result
            )
            
        except Exception as e:
            self.error_count += 1
            return None
    
    def calculate_checksum(self, data: List[int]) -> int:
        """
        Calculate checksum for message.
        
        Simple XOR checksum for error detection.
        
        Args:
            data: Message bytes
            
        Returns:
            8-bit checksum
        """
        checksum = 0
        for byte in data:
            checksum ^= byte
        return checksum
    
    def frame_message(self, payload: List[int]) -> List[int]:
        """
        Add framing (STX/ETX) to message.
        
        Args:
            payload: Message payload
            
        Returns:
            Framed message
        """
        return [self.STX] + payload + [self.ETX]
    
    def unframe_message(self, framed: List[int]) -> Optional[List[int]]:
        """
        Remove framing from message.
        
        Args:
            framed: Framed message
            
        Returns:
            Payload or None if invalid framing
        """
        if len(framed) < 2:
            return None
        
        if framed[0] != self.STX or framed[-1] != self.ETX:
            self.error_count += 1
            return None
        
        return framed[1:-1]
    
    def encode_status_request(self) -> List[int]:
        """Encode status request command."""
        # "STAT" in ASCII
        return [0x53, 0x54, 0x41, 0x54]
    
    def encode_status_response(
        self,
        hashes_computed: int,
        errors: int
    ) -> List[int]:
        """
        Encode status response.
        
        Args:
            hashes_computed: 64-bit counter
            errors: 24-bit error counter
            
        Returns:
            Status payload (10 bytes)
        """
        message = []
        
        # Hashes computed (8 bytes, big-endian)
        for i in range(7, -1, -1):
            message.append((hashes_computed >> (i * 8)) & 0xFF)
        
        # Errors (3 bytes, big-endian)
        for i in range(2, -1, -1):
            message.append((errors >> (i * 8)) & 0xFF)
        
        return message
    
    def get_statistics(self) -> Dict[str, int]:
        """Get protocol statistics."""
        return {
            'messages_sent': self.message_count,
            'errors': self.error_count
        }


class AVIDACCommand:
    """
    High-level commands for AVIDAC control.
    
    These commands are sent via the paper tape protocol
    to control the mining operation.
    """
    
    # Command codes
    CMD_START_MINING = 0x01
    CMD_STOP_MINING = 0x02
    CMD_RESET = 0x03
    CMD_GET_STATUS = 0x04
    CMD_SET_DIFFICULTY = 0x05
    CMD_GET_HASH_RATE = 0x06
    
    @staticmethod
    def encode(command: int, params: List[int] = None) -> List[int]:
        """
        Encode command for transmission.
        
        Format: [CMD][PARAM_COUNT][PARAM1]...[PARAMN]
        
        Args:
            command: Command code
            params: Optional parameters
            
        Returns:
            Encoded command bytes
        """
        params = params or []
        return [command, len(params)] + params
    
    @staticmethod
    def decode(data: List[int]) -> tuple:
        """
        Decode command from received data.
        
        Args:
            data: Command bytes
            
        Returns:
            (command_code, params) tuple
        """
        if len(data) < 2:
            return None, []
        
        command = data[0]
        param_count = data[1]
        
        if len(data) < 2 + param_count:
            return None, []
        
        params = data[2:2 + param_count]
        return command, params


if __name__ == '__main__':
    # Test protocol encoding/decoding
    protocol = PaperTapeProtocol()
    
    # Test mining job encoding
    job = MiningJob(
        job_id=12345,
        block_header=b'\x00' * 32,
        target=b'\xFF' * 32,
        timestamp=int(time.time())
    )
    
    encoded = protocol.encode_mining_job(job)
    print(f"Encoded job: {len(encoded)} bytes")
    
    decoded = protocol.decode_mining_job(encoded)
    if decoded:
        print(f"Decoded job ID: {decoded.job_id}")
        print(f"Job timestamp: {decoded.timestamp}")
    
    # Test solution encoding
    solution = Solution(
        job_id=12345,
        nonce=0x1234567890ABCDEF,
        hash_result=b'\xAB' * 32
    )
    
    encoded = protocol.encode_solution(solution)
    print(f"\nEncoded solution: {len(encoded)} bytes")
    
    decoded = protocol.decode_solution(encoded)
    if decoded:
        print(f"Decoded nonce: {decoded.nonce:016X}")
    
    print("\nProtocol test complete!")
