# 教程 04：智能合约开发 — RustChain 合约编程

> **难度：** 🟡 中等 | **预计时间：** 60 分钟 | **作者钱包：** zp6

---

## 概述

本教程介绍 RustChain 智能合约开发，包括开发环境配置、编写第一个合约、编译部署和与合约交互。

RustChain 智能合约使用 **Rust** 编写，编译为 WebAssembly (Wasm) 执行。

---

## 前置条件

- ✅ 已完成 [教程 01](./01-getting-started.md) 和 [教程 02](./02-first-transaction.md)
- ✅ 熟悉 Rust 基础语法
- ✅ 了解区块链智能合约基本概念
- ✅ 本地节点正在运行

---

## 步骤 1：安装合约开发工具

```bash
# 安装 rustchain-contract CLI（合约开发工具链）
cargo install rustchain-contract-cli

# 安装 Wasm 编译目标
rustup target add wasm32-unknown-unknown

# 验证安装
rustchain-contract --version
# rustchain-contract 0.3.0
```

---

## 步骤 2：创建合约项目

```bash
# 创建新合约项目
rustchain-contract new my-token
cd my-token

# 项目结构
# my-token/
# ├── Cargo.toml          # 项目配置和依赖
# ├── lib.rs              # 合约主代码
# └── .rustchain-contract # 合构配置
```

查看 `Cargo.toml`：

```toml
[package]
name = "my-token"
version = "0.1.0"
edition = "2021"

[dependencies]
rustchain-contract = { version = "0.3", features = ["std"] }
scale = { package = "parity-scale-codec", version = "3.0", features = ["derive"] }

[lib]
name = "my_token"
crate-type = ["cdylib"]

[profile.release]
opt-level = "z"     # 优化 Wasm 体积
lto = true
```

---

## 步骤 3：编写 ERC-20 代币合约

编辑 `lib.rs`：

```rust
#![cfg_attr(not(feature = "std"), no_std)]

use rustchain_contract::{
    contract, storage,
    Address, Balance, Env, Result,
};
use scale::{Decode, Encode};

/// 简单的 ERC-20 代币合约
#[contract]
pub struct MyToken {
    name: storage::Lazy<String>,
    symbol: storage::Lazy<String>,
    decimals: storage::Lazy<u8>,
    total_supply: storage::Lazy<Balance>,
    balances: storage::Mapping<Address, Balance>,
    allowances: storage::DoubleMapping<Address, Address, Balance>,
}

#[derive(Encode, Decode)]
pub struct TokenInfo {
    name: String,
    symbol: String,
    decimals: u8,
    total_supply: Balance,
}

impl MyToken {
    /// 初始化合约 — 部署时调用一次
    #[init]
    pub fn init(
        env: &mut Env,
        name: String,
        symbol: String,
        decimals: u8,
        initial_supply: Balance,
    ) -> Result<Self> {
        let caller = env.caller();

        let mut token = Self {
            name: storage::Lazy::new(),
            symbol: storage::Lazy::new(),
            decimals: storage::Lazy::new(),
            total_supply: storage::Lazy::new(),
            balances: storage::Mapping::new(),
            allowances: storage::DoubleMapping::new(),
        };

        token.name.set(&name)?;
        token.symbol.set(&symbol)?;
        token.decimals.set(&decimals)?;
        token.total_supply.set(&initial_supply)?;
        token.balances.insert(&caller, &initial_supply)?;

        // 触发 Transfer 事件（from = zero address 表示铸造）
        env.emit_event("Transfer", &[
            ("from", Address::zero()),
            ("to", caller),
            ("value", initial_supply),
        ]);

        Ok(token)
    }

    /// 查询代币信息
    #[view]
    pub fn token_info(&self) -> Result<TokenInfo> {
        Ok(TokenInfo {
            name: self.name.get()?,
            symbol: self.symbol.get()?,
            decimals: self.decimals.get()?,
            total_supply: self.total_supply.get()?,
        })
    }

    /// 查询余额
    #[view]
    pub fn balance_of(&self, owner: Address) -> Result<Balance> {
        self.balances.get(&owner).map(|b| b.unwrap_or(0))
    }

    /// 转账
    #[action]
    pub fn transfer(&mut self, env: &mut Env, to: Address, value: Balance) -> Result<()> {
        let caller = env.caller();
        let from_balance = self.balances.get(&caller)?.unwrap_or(0);

        if from_balance < value {
            return Err(rustchain_contract::Error::InsufficientBalance);
        }

        let to_balance = self.balances.get(&to)?.unwrap_or(0);

        self.balances.insert(&caller, &(from_balance - value))?;
        self.balances.insert(&to, &(to_balance + value))?;

        env.emit_event("Transfer", &[
            ("from", caller),
            ("to", to),
            ("value", value),
        ]);

        Ok(())
    }

    /// 授权额度
    #[action]
    pub fn approve(&mut self, env: &mut Env, spender: Address, value: Balance) -> Result<()> {
        let caller = env.caller();
        self.allowances.insert(&caller, &spender, &value)?;

        env.emit_event("Approval", &[
            ("owner", caller),
            ("spender", spender),
            ("value", value),
        ]);

        Ok(())
    }

    /// 授权转账
    #[action]
    pub fn transfer_from(
        &mut self,
        env: &mut Env,
        from: Address,
        to: Address,
        value: Balance,
    ) -> Result<()> {
        let caller = env.caller();
        let allowance = self.allowances.get(&from, &caller)?.unwrap_or(0);

        if allowance < value {
            return Err(rustchain_contract::Error::InsufficientAllowance);
        }

        let from_balance = self.balances.get(&from)?.unwrap_or(0);
        if from_balance < value {
            return Err(rustchain_contract::Error::InsufficientBalance);
        }

        let to_balance = self.balances.get(&to)?.unwrap_or(0);

        self.balances.insert(&from, &(from_balance - value))?;
        self.balances.insert(&to, &(to_balance + value))?;
        self.allowances.insert(&from, &caller, &(allowance - value))?;

        env.emit_event("Transfer", &[
            ("from", from),
            ("to", to),
            ("value", value),
        ]);

        Ok(())
    }
}
```

<!-- 📸 截图占位符：合约代码编辑器 -->
> 📸 **截图：** IDE 中的合约代码

---

## 步骤 4：编译合约

```bash
# 编译合约为 Wasm
rustchain-contract build

# 输出：
# 🔨 Compiling my-token...
#    Cargo build [wasm32-unknown-unknown]
#    Optimizing with wasm-opt
# ✅ Build successful!
#
# 📦 Output files:
#    target/contract/my_token.wasm    (3.2 KB)
#    target/contract/my_token.json    (ABI metadata)

# 检查 Wasm 体积（越小越好）
ls -la target/contract/my_token.wasm
```

<!-- 📸 截图占位符：编译输出 -->
> 📸 **截图：** 合约编译成功

---

## 步骤 5：部署合约

```bash
# 部署到本地开发网
rustchain-contract deploy \
  --wasm target/contract/my_token.wasm \
  --metadata target/contract/my_token.json \
  --account alice \
  --endpoint http://localhost:9933 \
  --args '["My Token", "MTK", 18, 1000000000000000000000000]'

# 输出：
# 📤 Deploying contract...
# 🆔 Contract address: rc1p4k8m2n...9qrst
# ✅ Deployment successful!
# 💰 Gas used: 12,345,678
# 💵 Deployment cost: 0.123 RC
```

<!-- 📸 截图占位符：合约部署成功 -->
> 📸 **截图：** 合约部署成功输出

---

## 步骤 6：与合约交互

```bash
# 查询代币信息（只读，不消耗 Gas）
rustchain-contract call \
  --contract rc1p4k8m2n...9qrst \
  --method token_info \
  --endpoint http://localhost:9933

# 输出：
# {
#   "name": "My Token",
#   "symbol": "MTK",
#   "decimals": 18,
#   "total_supply": 1000000000000000000000000
# }

# 查询余额
rustchain-contract call \
  --contract rc1p4k8m2n...9qrst \
  --method balance_of \
  --args '["rc1q7x8f2k...3mn9p"]' \
  --endpoint http://localhost:9933

# 转账（写入操作，消耗 Gas）
rustchain-contract call \
  --contract rc1p4k8m2n...9qrst \
  --account alice \
  --method transfer \
  --args '["rc1q9y3j4n...7kl2w", 1000000000000000000]' \
  --endpoint http://localhost:9933 \
  --gas 100000

# 输出：
# ✅ Transaction confirmed
# 💰 Gas used: 23,456
```

---

## 步骤 7：编写测试

```rust
// tests/test_token.rs
use rustchain_contract_test::{prelude::*, TestEnv};

#[test]
fn test_init_and_balance() {
    let mut env = TestEnv::new();
    let alice = env.create_account();

    let contract = MyToken::init(
        &mut env,
        "Test Token".into(),
        "TST".into(),
        18,
        1_000_000,
        alice,
    ).unwrap();

    assert_eq!(contract.balance_of(alice).unwrap(), 1_000_000);
}

#[test]
fn test_transfer() {
    let mut env = TestEnv::new();
    let alice = env.create_account();
    let bob = env.create_account();

    let mut contract = MyToken::init(
        &mut env, "Test".into(), "T".into(), 18, 1_000_000, alice,
    ).unwrap();

    contract.transfer(&mut env, bob, 500).unwrap();

    assert_eq!(contract.balance_of(alice).unwrap(), 999_500);
    assert_eq!(contract.balance_of(bob).unwrap(), 500);
}

#[test]
fn test_transfer_insufficient_balance() {
    let mut env = TestEnv::new();
    let alice = env.create_account();
    let bob = env.create_account();

    let mut contract = MyToken::init(
        &mut env, "Test".into(), "T".into(), 18, 100, alice,
    ).unwrap();

    let result = contract.transfer(&mut env, bob, 200);
    assert!(result.is_err());
}
```

```bash
# 运行测试
cargo test

# running 3 tests
# test test_init_and_balance ... ok
# test test_transfer ... ok
# test test_transfer_insufficient_balance ... ok
```

---

## 常见问题 (FAQ)

### Q: 合约编译报 `wasm32-unknown-unknown` 找不到？
**A:** 运行 `rustup target add wasm32-unknown-unknown`。

### Q: 部署时 Gas 不够怎么办？
**A:** 增加 Gas limit：`--gas 500000`。如果合约初始化逻辑复杂，可能需要更多 Gas。

### Q: 如何调试合约？
**A:** 使用测试环境进行单元测试，或在本地节点上使用 `rustchain-contract call --dry-run` 模拟执行。

### Q: 合约可以升级吗？
**A:** 默认不可变。可以使用代理模式（Proxy Pattern）实现可升级合约。

### Q: 存储费用如何计算？
**A:** 按字节计费。每字节存储约 0.001 RC/天。尽量压缩存储数据。

### Q: 合约大小有限制吗？
**A:** 单个合约 Wasm 最大 256 KB。超过时考虑拆分为多个合约。

---

## 下一步

🎉 你已经完成了第一个 RustChain 智能合约！

接下来，请继续学习：
- **[教程 05：高级主题](./05-advanced-topics.md)** — 跨合约调用、Gas 优化、安全最佳实践

---

*本教程由 [zp6](https://github.com/zp6) 贡献至 RustChain 社区。*
