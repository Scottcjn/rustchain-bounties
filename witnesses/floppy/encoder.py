import zlib
import struct

def encode_epoch_proof(proof_data: bytes) -> bytes:
    """
    Compresses and serializes an epoch proof to fit within the 1.44MB constraint of a standard 3.5" floppy disk.
    Uses zlib compression level 9 (max) for extreme density.
    """
    compressed = zlib.compress(proof_data, level=9)
    if len(compressed) > 1474560:
        raise ValueError("Proof payload exceeds 1.44MB physical media limit.")
    
    # 1 byte magic + 4 bytes length + payload
    header = struct.pack('>BI', 0xFD, len(compressed))
    return header + compressed

if __name__ == "__main__":
    dummy_proof = b"0" * 2000000 # 2MB dummy proof
    print(f"Original size: {len(dummy_proof)} bytes")
    encoded = encode_epoch_proof(dummy_proof)
    print(f"Floppy-ready size: {len(encoded)} bytes")
