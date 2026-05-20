# RustChain 测试指南

## 概述

本指南详细介绍 RustChain 项目的测试策略。RustChain 是一个以 Python 为主的项目（pyproject.toml 管理依赖），Rust 代码仅存在于 `rustchain-wallet` 子目录。

---

## 1. 项目结构与测试架构

```
rustchain-bounties/
├── node/                  # Python 核心模块
│   ├── utxo_db.py
│   ├── governance.py
│   ├── hardware_fingerprint.py
│   └── ...
├── scripts/               # 工具脚本
├── tools/                 # CLI 工具
├── tests/                 # Python 测试
│   ├── test_utxo_db.py
│   ├── test_health_check.py
│   └── ...
├── rustchain-wallet/      # Rust 钱包组件
│   ├── src/
│   ├── Cargo.toml
│   └── tests/
├── pyproject.toml         # Python 项目配置
├── requirements.txt
└── pytest.ini
```

### 测试金字塔

```
        /  API Tests     \       ← 少量，测试 rustchain.org 端点
       /--------------------\
      /  Integration Tests  \    ← 适量，测试模块间交互
     /------------------------\
    /     Unit Tests           \  ← 大量，快，细粒度
   /----------------------------\
```

---

## 2. Python 单元测试

### 2.1 基本结构

```python
import pytest
from node.utxo_db import UTXODatabase

def test_utxo_add_and_get():
    """Test adding and retrieving UTXO entries."""
    db = UTXODatabase(":memory:")
    db.add_utxo("tx1", 0, "alice", 1000)

    utxo = db.get_utxo("tx1", 0)
    assert utxo is not None
    assert utxo["address"] == "alice"
    assert utxo["amount"] == 1000

def test_utxo_spend():
    """Test spending a UTXO marks it as spent."""
    db = UTXODatabase(":memory:")
    db.add_utxo("tx1", 0, "alice", 1000)

    db.spend_utxo("tx1", 0)

    utxo = db.get_utxo("tx1", 0)
    assert utxo["spent"] is True

def test_double_spend_rejected():
    """Test that double-spending a UTXO raises an error."""
    db = UTXODatabase(":memory:")
    db.add_utxo("tx1", 0, "alice", 500)

    db.spend_utxo("tx1", 0)
    with pytest.raises(ValueError, match="already spent"):
        db.spend_utxo("tx1", 0)
```

### 2.2 测试硬件指纹

```python
from node.hardware_fingerprint import generate_fingerprint

def test_fingerprint_deterministic():
    """Same hardware should produce same fingerprint."""
    fp1 = generate_fingerprint(arch="ppc", model="G4", serial="ABC123")
    fp2 = generate_fingerprint(arch="ppc", model="G4", serial="ABC123")
    assert fp1 == fp2

def test_fingerprint_differs_by_arch():
    """Different architectures produce different fingerprints."""
    fp_ppc = generate_fingerprint(arch="ppc", model="G4", serial="ABC123")
    fp_sparc = generate_fingerprint(arch="sparc", model="Ultra", serial="ABC123")
    assert fp_ppc != fp_sparc
```

### 2.3 使用 pytest fixtures

```python
import pytest
import sqlite3

@pytest.fixture
def test_db():
    """Create an in-memory test database."""
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE miners (
            miner_id TEXT PRIMARY KEY,
            arch TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    yield conn
    conn.close()

def test_miner_registration(test_db):
    test_db.execute(
        "INSERT INTO miners (miner_id, arch) VALUES (?, ?)",
        ("miner-001", "ppc")
    )
    test_db.commit()

    cursor = test_db.execute("SELECT * FROM miners WHERE miner_id = ?", ("miner-001",))
    row = cursor.fetchone()
    assert row is not None
    assert row[1] == "ppc"
```

---

## 3. Python 集成测试

### 3.1 API 集成测试

```python
import pytest
import requests

BASE_URL = "https://rustchain.org"

@pytest.mark.integration
def test_health_endpoint():
    """Test the /health endpoint returns valid response."""
    resp = requests.get(f"{BASE_URL}/health", timeout=10)
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data

@pytest.mark.integration
def test_miners_endpoint():
    """Test the /api/miners endpoint."""
    resp = requests.get(f"{BASE_URL}/api/miners", timeout=10)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)

@pytest.mark.integration
def test_wallet_balance():
    """Test the /wallet/balance endpoint."""
    resp = requests.get(
        f"{BASE_URL}/wallet/balance",
        params={"address": "test-address"},
        timeout=10,
    )
    assert resp.status_code == 200
```

### 3.2 SQLite WAL 模式测试

```python
import sqlite3
import threading

def test_concurrent_reads():
    """Test SQLite WAL mode handles concurrent reads."""
    conn = sqlite3.connect("test.db")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("CREATE TABLE IF NOT EXISTS epochs (id INTEGER PRIMARY KEY, settled INTEGER)")
    conn.execute("INSERT INTO epochs (id, settled) VALUES (1, 0)")
    conn.commit()

    results = []
    def read_epoch():
        c = sqlite3.connect("test.db")
        row = c.execute("SELECT * FROM epochs WHERE id = 1").fetchone()
        results.append(row)
        c.close()

    threads = [threading.Thread(target=read_epoch) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(results) == 10
    conn.close()
    import os; os.unlink("test.db")
```

---

## 4. Rust 钱包测试

Rust 代码位于 `rustchain-wallet/` 子目录，使用标准的 Cargo 测试：

### 4.1 运行 Rust 测试

```bash
# 从项目根目录运行（需要指定 working directory）
cd rustchain-wallet
cargo test

# 或者从根目录
cargo test --manifest-path rustchain-wallet/Cargo.toml
```

### 4.2 Rust 单元测试示例

```rust
// rustchain-wallet/src/lib.rs

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_address_generation() {
        let wallet = Wallet::new();
        let addr = wallet.generate_address();
        assert!(addr.starts_with("rc1"));
    }

    #[test]
    fn test_signature_roundtrip() {
        let wallet = Wallet::new();
        let message = b"test attestation";
        let sig = wallet.sign(message);
        assert!(wallet.verify(message, &sig));
    }
}
```

---

## 5. 运行测试

### 5.1 Python 测试命令

```bash
# 安装依赖
pip install -r requirements.txt
pip install pytest pytest-cov

# 运行所有测试
pytest

# 运行特定模块
pytest tests/test_utxo_db.py

# 运行带标记的测试
pytest -m integration

# 带覆盖率
pytest --cov=node --cov=scripts --cov-report=html

# 详细输出
pytest -v
```

### 5.2 Rust 测试命令

```bash
# 运行 Rust 钱包测试
cd rustchain-wallet
cargo test

# 带输出
cargo test -- --nocapture

# 运行特定测试
cargo test test_address_generation
```

### 5.3 CI 配置

```yaml
# GitHub Actions 示例
jobs:
  test-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt pytest pytest-cov
      - run: pytest --cov

  test-rust:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-rust@v1
      - working-directory: rustchain-wallet
        run: cargo test
```

---

## 6. 覆盖率与质量

### 6.1 覆盖率目标

| 模块 | 最低覆盖率 | 目标覆盖率 |
|------|-----------|-----------|
| node/ (Python) | 70% | 85%+ |
| scripts/ (Python) | 60% | 80%+ |
| rustchain-wallet (Rust) | 70% | 85%+ |

### 6.2 质量门禁

- 所有 PR 必须通过 `pytest`
- Python 代码通过 `ruff check` 无警告
- Rust 钱包通过 `cargo clippy` 无警告
- Rust 代码 `cargo fmt --check` 格式正确
- 新代码覆盖率不低于模块平均值

---

## 7. 最佳实践

1. **使用内存数据库**：测试时用 SQLite `:memory:` 避免文件清理问题
2. **确定性**：测试结果不依赖外部 API 调用（使用 mock 或标记为 integration）
3. **独立性**：测试之间无依赖，可并行运行
4. **边界条件**：测试零值、空集、溢出、并发等边界场景
5. **失败模式**：测试错误路径，验证错误信息有意义
6. **markers**：使用 `@pytest.mark.integration` 标记需要网络的测试
7. **fixtures**：复用数据库连接和测试数据
8. **定期清理**：删除过时测试，重构脆弱测试
