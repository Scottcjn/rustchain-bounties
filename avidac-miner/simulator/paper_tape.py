"""
Paper Tape I/O Simulator

Simulates paper tape input/output for AVIDAC.
Paper tape was the primary I/O medium for early computers like AVIDAC.

Paper tape protocol:
- Binary data encoded as ASCII hex
- STX (0x02) marks start of message
- ETX (0x03) marks end of message
- Typical speed: 100 characters/second
"""

import time
from typing import Optional, List, Dict, Any, Union
from pathlib import Path


class PaperTapeIO:
    """
    Simulates paper tape input/output for AVIDAC.
    
    Paper tape was a punched paper strip with holes representing data.
    AVIDAC used paper tape for:
    - Program loading
    - Data input
    - Result output
    
    This simulator supports:
    - ASCII hex encoding (human readable)
    - Binary encoding (efficient)
    - Virtual tape files
    """
    
    # Control characters
    STX = 0x02  # Start of transmission
    ETX = 0x03  # End of transmission
    NUL = 0x00  # Null/padding
    
    def __init__(
        self,
        encoding: str = 'hex',
        speed_chars_per_sec: float = 100.0,
        simulate_delays: bool = True
    ):
        """
        Initialize paper tape I/O.
        
        Args:
            encoding: 'hex' (ASCII hex) or 'binary' (raw bytes)
            speed_chars_per_sec: Simulated tape speed
            simulate_delays: Whether to simulate read/write delays
        """
        self.encoding = encoding
        self.speed = speed_chars_per_sec
        self.simulate_delays = simulate_delays
        
        # Input tape (data to be read by AVIDAC)
        self.input_tape: List[int] = []
        self.input_position = 0
        
        # Output tape (data punched by AVIDAC)
        self.output_tape: List[int] = []
        
        # Statistics
        self.chars_read = 0
        self.chars_written = 0
        self.read_errors = 0
        
        # Timing
        self.last_read_time = 0.0
        self.last_write_time = 0.0
    
    def _simulate_delay(self, chars: int) -> None:
        """Simulate paper tape read/write delay."""
        if self.simulate_delays:
            delay = chars / self.speed
            time.sleep(delay)
    
    def load_tape(self, data: Union[str, bytes, List[int]]) -> None:
        """
        Load data onto input tape.
        
        Args:
            data: String, bytes, or list of integers
        """
        if isinstance(data, str):
            if self.encoding == 'hex':
                # Parse hex string
                self.input_tape = [int(data[i:i+2], 16) for i in range(0, len(data), 2)]
            else:
                self.input_tape = [ord(c) for c in data]
        elif isinstance(data, bytes):
            self.input_tape = list(data)
        else:
            self.input_tape = data
        
        self.input_position = 0
    
    def load_from_file(self, filepath: Union[str, Path]) -> None:
        """
        Load tape from file.
        
        Args:
            filepath: Path to tape file
        """
        filepath = Path(filepath)
        with open(filepath, 'rb') as f:
            data = f.read()
        
        if self.encoding == 'hex':
            # Decode hex file
            text = data.decode('ascii').strip()
            self.input_tape = [int(text[i:i+2], 16) for i in range(0, len(text), 2)]
        else:
            self.input_tape = list(data)
        
        self.input_position = 0
    
    def save_to_file(self, filepath: Union[str, Path]) -> None:
        """
        Save output tape to file.
        
        Args:
            filepath: Path to output file
        """
        filepath = Path(filepath)
        
        if self.encoding == 'hex':
            # Save as hex string
            hex_str = ''.join(f'{b:02X}' for b in self.output_tape)
            with open(filepath, 'w') as f:
                f.write(hex_str)
        else:
            with open(filepath, 'wb') as f:
                f.write(bytes(self.output_tape))
    
    def read_char(self) -> Optional[int]:
        """
        Read one character from input tape.
        
        Returns:
            Character (0-255) or None if end of tape
        """
        if self.input_position >= len(self.input_tape):
            return None
        
        char = self.input_tape[self.input_position]
        self.input_position += 1
        self.chars_read += 1
        self.last_read_time = time.time()
        
        return char
    
    def read_word(self, bytes_count: int = 5) -> Optional[int]:
        """
        Read a 40-bit word (5 bytes) from tape.
        
        Args:
            bytes_count: Number of bytes to read (default 5 for 40 bits)
        
        Returns:
            40-bit integer or None if insufficient data
        """
        if self.encoding == 'hex':
            # Read hex representation (10 hex chars = 5 bytes = 40 bits)
            hex_chars = []
            for _ in range(bytes_count * 2):
                char = self.read_char()
                if char is None:
                    return None
                hex_chars.append(chr(char))
            
            return int(''.join(hex_chars), 16)
        else:
            # Read raw bytes
            value = 0
            for i in range(bytes_count):
                char = self.read_char()
                if char is None:
                    return None
                value = (value << 8) | char
            return value
    
    def punch_char(self, char: int) -> None:
        """
        Punch one character to output tape.
        
        Args:
            char: Character to punch (0-255)
        """
        self.output_tape.append(char & 0xFF)
        self.chars_written += 1
        self.last_write_time = time.time()
    
    def punch_word(self, value: int, bytes_count: int = 5) -> None:
        """
        Punch a 40-bit word to tape.
        
        Args:
            value: 40-bit integer
            bytes_count: Number of bytes (default 5 for 40 bits)
        """
        if self.encoding == 'hex':
            # Convert to hex string
            hex_str = f'{value:0{bytes_count * 2}X}'
            for char in hex_str:
                self.punch_char(ord(char))
        else:
            # Convert to bytes (big-endian)
            for i in range(bytes_count - 1, -1, -1):
                byte = (value >> (i * 8)) & 0xFF
                self.punch_char(byte)
    
    def read_message(self) -> Optional[List[int]]:
        """
        Read a complete message (STX ... ETX).
        
        Returns:
            List of bytes (excluding STX/ETX) or None if invalid
        """
        # Wait for STX
        while True:
            char = self.read_char()
            if char is None:
                return None
            if char == self.STX:
                break
        
        # Read data until ETX
        data = []
        while True:
            char = self.read_char()
            if char is None:
                return None  # Unexpected end
            if char == self.ETX:
                break
            data.append(char)
        
        return data
    
    def write_message(self, data: List[int]) -> None:
        """
        Write a complete message with STX/ETX framing.
        
        Args:
            data: List of bytes to send
        """
        self.punch_char(self.STX)
        for byte in data:
            self.punch_char(byte)
        self.punch_char(self.ETX)
    
    def encode_nonce(self, nonce: int) -> List[int]:
        """
        Encode 64-bit nonce for transmission.
        
        Args:
            nonce: 64-bit nonce value
        
        Returns:
            List of bytes (8 bytes, big-endian)
        """
        return [(nonce >> (i * 8)) & 0xFF for i in range(7, -1, -1)]
    
    def decode_nonce(self, data: List[int]) -> int:
        """
        Decode 64-bit nonce from received data.
        
        Args:
            data: List of 8 bytes
        
        Returns:
            64-bit nonce value
        """
        nonce = 0
        for byte in data:
            nonce = (nonce << 8) | byte
        return nonce
    
    def reset_input(self) -> None:
        """Reset input tape to beginning."""
        self.input_position = 0
    
    def clear_output(self) -> None:
        """Clear output tape."""
        self.output_tape = []
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get paper tape I/O status.
        
        Returns:
            Dictionary with status information
        """
        return {
            'encoding': self.encoding,
            'speed_chars_per_sec': self.speed,
            'input': {
                'length': len(self.input_tape),
                'position': self.input_position,
                'remaining': len(self.input_tape) - self.input_position,
                'percent_complete': (self.input_position / max(1, len(self.input_tape))) * 100
            },
            'output': {
                'length': len(self.output_tape)
            },
            'statistics': {
                'chars_read': self.chars_read,
                'chars_written': self.chars_written,
                'read_errors': self.read_errors
            },
            'timing': {
                'last_read_time': self.last_read_time,
                'last_write_time': self.last_write_time
            }
        }
    
    def get_output_hex(self) -> str:
        """Get output tape as hex string."""
        return ''.join(f'{b:02X}' for b in self.output_tape)
    
    def get_output_text(self) -> str:
        """Get output tape as text (if printable)."""
        try:
            return bytes(self.output_tape).decode('ascii')
        except UnicodeDecodeError:
            return self.get_output_hex()


class PaperTapeProtocol:
    """
    Implements the paper tape communication protocol.
    
    Protocol format:
    Request (AVIDAC → Bridge):
        [STX][NONCE_7][NONCE_6]...[NONCE_0][ETX]
    
    Response (Bridge → AVIDAC):
        [STX][RESULT_7][RESULT_6]...[RESULT_0][ETX]
    """
    
    def __init__(self, tape_io: PaperTapeIO):
        """
        Initialize protocol handler.
        
        Args:
            tape_io: PaperTapeIO instance
        """
        self.tape = tape_io
    
    def send_nonce(self, nonce: int) -> None:
        """
        Send 64-bit nonce to AVIDAC.
        
        Args:
            nonce: 64-bit nonce value
        """
        data = self.tape.encode_nonce(nonce)
        self.tape.write_message(data)
    
    def receive_nonce(self) -> Optional[int]:
        """
        Receive 64-bit nonce from AVIDAC.
        
        Returns:
            64-bit nonce or None if error
        """
        data = self.tape.read_message()
        if data is None or len(data) != 8:
            return None
        return self.tape.decode_nonce(data)
    
    def send_result(self, result: int) -> None:
        """
        Send 64-bit result to AVIDAC.
        
        Args:
            result: 64-bit result value
        """
        data = self.tape.encode_nonce(result)
        self.tape.write_message(data)
    
    def receive_result(self) -> Optional[int]:
        """
        Receive 64-bit result from AVIDAC.
        
        Returns:
            64-bit result or None if error
        """
        data = self.tape.read_message()
        if data is None or len(data) != 8:
            return None
        return self.tape.decode_nonce(data)
