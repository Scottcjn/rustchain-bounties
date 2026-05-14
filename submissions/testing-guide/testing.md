# RustChain 测试指南

## 概述

本指南详细介绍 RustChain 项目的测试策略，涵盖单元测试、集成测试和端到端（E2E）测试的最佳实践。

---

## 1. 测试架构总览

```
rustchain/
├── crates/
│   ├── chain/          # 核心链逻辑
│   │   ├── src/
│   │   └── tests/      # 集成测试
│   ├── consensus/      # 共识模块
│   │   ├── src/
│   │   └── tests/
│   ├── contracts/      # 智能合约运行时
│   └── sdk/            # SDK
├── tests/              # E2E 测试
│   ├── integration/
│   └── e2e/
└── Cargo.toml
```

### 测试金字塔

```
        ╱  E2E Tests  ╲        ← 少量，慢，高置信度
       ╱────────────────╲
      ╱ Integration Tests ╲    ← 适量，中等速度
     ╱────────────────────╲
    ╱     Unit Tests       ╲   ← 大量，快，细粒度
   ╱────────────────────────╲
```

---

## 2. 单元测试

### 2.1 基本结构

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_transfer_balance() {
        let mut state = State::new();
        state.set_balance("alice", 1000);
        state.set_balance("bob", 0);

        state.transfer("alice", "bob", 500).unwrap();

        assert_eq!(state.get_balance("alice"), 500);
        assert_eq!(state.get_balance("bob"), 500);
    }

    #[test]
    fn test_insufficient_balance() {
        let mut state = State::new();
        state.set_balance("alice", 100);

        let result = state.transfer("alice", "bob", 200);
        assert!(result.is_err());
        assert_eq!(state.get_balance("alice"), 100); // 不变
    }
}
```

### 2.2 测试交易处理

```rust
#[test]
fn test_transaction_signature_verification() {
    let (sk, pk) = generate_keypair();
    let tx = Transaction::new_transfer("alice", "bob", 100);
    let signed_tx = tx.sign(&sk);

    assert!(signed_tx.verify(&pk));
}

#[test]
fn test_invalid_signature_rejected() {
    let (sk1, _) = generate_keypair();
    let (_, pk2) = generate_keypair();
    let tx = Transaction::new_transfer("alice", "bob", 100);
    let signed_tx = tx.sign(&sk1);

    assert!(!signed_tx.verify(&pk2)); // 用错误的公钥验证
}
```

### 2.3 测试状态机

```rust
#[test]
fn test_state_transition() {
    let mut sm = StateMachine::new();

    // 初始状态
    assert_eq!(sm.current_height(), 0);

    // 应用有效区块
    let block = Block::new(1, vec![tx1, tx2], &validator_key);
    sm.apply_block(block).unwrap();

    assert_eq!(sm.current_height(), 1);
    assert_eq!(sm.get_balance("bob"), 200);
}

#[test]
fn test_double_spend_rejected() {
    let mut sm = StateMachine::new();
    sm.set_balance("alice", 100);

    let tx1 = Transaction::transfer("alice", "bob", 80);
    let tx2 = Transaction::transfer("alice", "charlie", 80); // 同一 nonce

    sm.apply_transaction(tx1).unwrap();
    let result = sm.apply_transaction(tx2);
    assert!(result.is_err()); // 双花拒绝
}
```

---

## 3. 集成测试

### 3.1 测试目录结构

```rust
// tests/chain_integration.rs
use rustchain::test_utils::*;

#[tokio::test]
async fn test_full_block_lifecycle() {
    // 启动测试网络
    let network = TestNetwork::new(4).await;

    // 提交交易
    let tx = network.create_transfer("alice", "bob", 1000);
    network.submit_transaction(tx).await.unwrap();

    // 等待出块
    network.wait_for_height(1).await;

    // 验证状态
    assert_eq!(network.query_balance("bob").await, 1000);
}

#[tokio::test]
async fn test_consensus_with_byzantine() {
    let mut network = TestNetwork::new(4).await;
    network.set_byzantine(1, ByzantineBehavior::DoubleVote);

    // 网络仍应达成共识（BFT 容忍 1/3）
    network.submit_transaction(simple_tx()).await.unwrap();
    network.wait_for_finalization(1).await;
}
```

### 3.2 合约集成测试

```rust
#[tokio::test]
async fn test_contract_deploy_and_call() {
    let network = TestNetwork::new(1).await;

    // 部署合约
    let code = wasm_contract("test_contract.wasm");
    let contract_addr = network.deploy_contract(
        "deployer",
        code,
        &["initial_value": "42"]
    ).await.unwrap();

    // 调用合约
    let result = network.query_contract(
        &contract_addr,
        "get_value"
    ).await.unwrap();
    assert_eq!(result, "42");

    // 修改状态
    network.execute_contract(
        "user1",
        &contract_addr,
        "set_value",
        &["100"]
    ).await.unwrap();

    let result = network.query_contract(
        &contract_addr,
        "get_value"
    ).await.unwrap();
    assert_eq!(result, "100");
}
```

### 3.3 P2P 网络测试

```rust
#[tokio::test]
async fn test_peer_discovery_and_gossip() {
    let network = TestNetwork::new(5).await;

    // 验证所有节点互相发现
    for node in network.nodes() {
        let peers = node.get_peers().await;
        assert!(peers.len() >= 3);
    }

    // 广播交易验证传播
    let tx = network.nodes()[0].create_transfer("a", "b", 100);
    network.nodes()[0].broadcast_tx(tx.clone()).await;

    tokio::time::sleep(Duration::from_secs(2)).await;

    // 所有节点应收到交易
    for node in network.nodes() {
        let mempool = node.get_mempool().await;
        assert!(mempool.contains(&tx.hash()));
    }
}
```

---

## 4. 端到端（E2E）测试

### 4.1 测试框架

使用 `test-framework` crate 提供完整的 E2E 测试环境：

```rust
// tests/e2e/full_scenario.rs
use rustchain_test_framework::*;

#[tokio::test]
#[serial_test::serial]
async fn test_e2e_transfer_scenario() {
    // 1. 启动本地网络
    let env = TestEnv::builder()
        .with_validators(4)
        .with_genesis_accounts(vec![
            ("alice", 1_000_000_000),
            ("bob", 0),
        ])
        .build()
        .await;

    // 2. 查询初始余额
    let alice_balance = env.query_balance("alice").await;
    assert_eq!(alice_balance, 1_000_000_000);

    // 3. 发送转账
    let tx_hash = env.send_transfer("alice", "bob", 500_000).await;

    // 4. 等待确认
    env.wait_for_tx_confirmation(&tx_hash).await;

    // 5. 验证最终状态
    assert_eq!(env.query_balance("alice").await, 999_500_000);
    assert_eq!(env.query_balance("bob").await, 500_000);
}
```

### 4.2 升级场景测试

```rust
#[tokio::test]
async fn test_e2e_chain_upgrade() {
    let mut env = TestEnv::builder()
        .with_validators(4)
        .build()
        .await;

    // 在升级前提交交易
    env.send_transfer("alice", "bob", 1000).await;
    let pre_height = env.current_height().await;

    // 触发升级
    env.propose_upgrade("v2.0.0", pre_height + 10).await;
    env.vote_on_upgrade("v2.0.0", Vote::Yes).await;

    // 等待升级执行
    env.wait_for_height(pre_height + 10).await;

    // 验证升级后链正常运行
    env.send_transfer("bob", "alice", 500).await;
    assert!(env.is_node_healthy().await);
}
```

### 4.3 压力测试

```rust
#[tokio::test]
async fn test_e2e_stress_high_tps() {
    let env = TestEnv::builder()
        .with_validators(4)
        .with_genesis_accounts(vec![
            ("sender", 100_000_000_000),
        ])
        .build()
        .await;

    // 并发提交 1000 笔交易
    let mut handles = vec![];
    for i in 0..1000 {
        let env_clone = env.clone();
        handles.push(tokio::spawn(async move {
            env_clone.send_transfer(
                "sender",
                &format!("receiver_{}", i),
                1000
            ).await
        }));
    }

    // 等待所有交易完成
    for h in handles {
        h.await.unwrap().unwrap();
    }

    // 等待所有交易上链
    env.wait_for_mempool_empty().await;

    let stats = env.get_performance_stats().await;
    println!("Average TPS: {}", stats.tps);
    println!("P99 latency: {}ms", stats.p99_latency_ms);
    assert!(stats.success_rate > 0.99);
}
```

---

## 5. 测试工具与辅助

### 5.1 Mock 工具

```rust
use rustchain_test_utils::mocks::*;

// Mock 时间
mock_time!(MockClock, 1700000000);

// Mock 网络
let mock_net = MockNetwork::new();
mock_net.set_latency(Duration::from_millis(100));
mock_net.set_packet_loss(0.01); // 1% 丢包

// Mock 存储
let mock_store = MockStore::new();
mock_store.set("key", b"value");
```

### 5.2 测试数据生成

```rust
use rustchain_test_utils::generators::*;

// 随机交易生成器
let tx_gen = TransactionGenerator::new()
    .with_transfer_count(100)
    .with_max_amount(10_000);

// 随机区块生成器
let block_gen = BlockGenerator::new()
    .with_transactions(tx_gen.generate())
    .with_valid_gap(2..5);
```

### 5.3 断言辅助

```rust
use rustchain_test_utils::assertions::*;

// 区块链专用断言
assert_eventually_eq!(
    env.query_balance("bob").await,
    1000,
    timeout = Duration::from_secs(10),
);

assert_no_panics!(state.apply_transaction(tx));

assert_consensus_reached!(&network, height: 5, timeout: 30s);
```

---

## 6. 运行测试

### 6.1 常用命令

```bash
# 运行所有单元测试
cargo test

# 运行特定模块
cargo test -p rustchain-chain

# 运行集成测试
cargo test --test integration

# 运行 E2E 测试（需要环境）
cargo test --test e2e -- --ignored

# 带覆盖率
cargo tarpaulin --out Html

# 仅检查编译（快速）
cargo check --tests
```

### 6.2 CI 中的测试配置

```bash
# 快速反馈：单元测试
cargo test --lib -- -j4

# 完整测试：单元 + 集成
cargo test --workspace

# Nightly：E2E 测试
cargo test --test e2e -- --ignored
```

### 6.3 测试环境变量

```bash
# 控制测试行为
export RUSTCHAIN_TEST_TIMEOUT=60
export RUSTCHAIN_TEST_LOG=debug
export RUSTCHAIN_TEST_NETWORK_SIZE=4
```

---

## 7. 覆盖率与质量

### 7.1 覆盖率目标

| 模块 | 最低覆盖率 | 目标覆盖率 |
|------|-----------|-----------|
| 核心链逻辑 | 80% | 90%+ |
| 共识引擎 | 85% | 95%+ |
| 合约运行时 | 80% | 90%+ |
| SDK | 70% | 85%+ |
| P2P 网络 | 60% | 80%+ |

### 7.2 质量门禁

- 所有 PR 必须通过 `cargo test`
- `cargo clippy` 无警告
- `cargo fmt --check` 格式正确
- 新代码覆盖率不低于模块平均值
- 关键路径必须有集成测试覆盖

---

## 8. 最佳实践

1. **测试先行**：复杂逻辑先写测试再实现
2. **确定性**：测试结果不依赖时间、随机数（除非明确 mock）
3. **独立性**：测试之间无依赖，可并行运行
4. **可读性**：测试命名描述行为，使用 `describe - should - when` 模式
5. **边界条件**：测试零值、空集、溢出、并发等边界场景
6. **失败模式**：测试错误路径，验证错误信息有意义
7. **性能回归**：关键路径添加基准测试（`cargo bench`）
8. **定期清理**：删除过时测试，重构脆弱测试
