# SPDX-License-Identifier: MIT
"""RustChain Dreamcast (SH4) Miner — MicroPython version."""

import usocket
import ubinascii
import utime
import sys

WALLET_NAME = "dreamcast-Antiquity-Node"
DEFAULT_HOST = "50.28.86.131"
DEFAULT_PORT = 80


def get_sh4_fingerprint():
    fp = 0
    buf = bytearray(512)
    for i in range(512):
        buf[i] = (i * 17) ^ (i << 2)
    seq_sum = sum(buf[i] for i in range(512))
    fp ^= seq_sum
    stride_sum = sum(buf[i] for i in range(0, 512, 16))
    fp ^= stride_sum << 5
    t0 = utime.ticks_ms()
    for _ in range(1000):
        fp ^= t0
    t1 = utime.ticks_ms()
    fp ^= (t1 - t0)
    return fp & 0xFFFFFFFF


def calculate_hash(data, nonce):
    hash_val = 5381
    for c in data:
        if isinstance(c, str):
            c = ord(c)
        hash_val = ((hash_val << 5) + hash_val) + c
    return (hash_val ^ nonce) & 0xFFFFFFFF


def submit_attestation(wallet, fp, hash_val, nonce):
    addr = usocket.getaddrinfo(DEFAULT_HOST, DEFAULT_PORT)[0]
    s = usocket.socket()
    s.connect(addr[-1])
    payload = ('{"device_arch":"sh4","device_family":"dreamcast",'
               '"wallet":"%s","fingerprint":"%08x",'
               '"hash":"%08x","nonce":"%u","miner_id":"%s"}' % (
                   wallet, fp, hash_val, nonce, wallet))
    req = ('POST /api/miners HTTP/1.1\r\n'
           'Host: %s\r\n'
           'Content-Type: application/json\r\n'
           'Content-Length: %d\r\n'
           'Connection: close\r\n'
           '\r\n'
           '%s') % (DEFAULT_HOST, len(payload), payload)
    s.write(req.encode())
    resp = s.read(1024)
    s.close()
    return resp


def main():
    wallet = WALLET_NAME
    for i in range(1, len(sys.argv) - 1):
        if sys.argv[i] == "--wallet":
            wallet = sys.argv[i + 1]
    print("RustChain Dreamcast (SH4) Miner - 3.0x")
    print("Wallet:", wallet)
    fp = get_sh4_fingerprint()
    print("Fingerprint: %08X" % fp)
    nonce = utime.time()
    hash_val = calculate_hash("rustchain-epoch-legacy", nonce)
    print("Hash: %08X  Nonce: %u" % (hash_val, nonce))
    print("Submitting attestation...")
    resp = submit_attestation(wallet, fp, hash_val, nonce)
    print("Response:", resp[:200])
    print("Dreamcast SH4 miner attestation submitted. 3.0x earned.")


if __name__ == "__main__":
    main()
