#!/usr/bin/env python
"""Test basic imports and structure."""

import sys
sys.path.insert(0, ".")

# Test imports
try:
    from rustchain import RustChainClient
    from rustchain.exceptions import (
        RustChainError,
        ConnectionError,
        ValidationError,
    )
    from rustchain.models import (
        HealthStatus,
        EpochInfo,
        Miner,
        Balance,
        TransferResult,
        Block,
        Transaction,
    )
    print("[OK] All imports successful!")
    
    # Test client instantiation
    client = RustChainClient()
    print(f"[OK] Client created: {client.base_url}")
    
    # Test model creation
    health = HealthStatus(status="healthy")
    print(f"[OK] HealthStatus model: {health.status}")
    
    epoch = EpochInfo(current_epoch=100, start_height=1000)
    print(f"[OK] EpochInfo model: epoch {epoch.current_epoch}")
    
    print("\n[SUCCESS] All basic tests passed!")
    
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)