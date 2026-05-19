# 教程 05：高级主题 — RustChain 深度开发

> **难度：** 🔴 进阶 | **预计时间：** 90 分钟 | **作者钱包：** zp6

---

## 概述

本教程涵盖 RustChain 高级开发主题，包括跨合约调用、自定义 Runtime 模块、Gas 优化策略和安全最佳实践。

---

## 前置条件

- ✅ 已完成 [教程 01-04](./01-getting-started.md)
- ✅ 熟练掌握 Rust 语言
- ✅ 理解 RustChain 智能合约架构
- ✅ 了解 Wasm 执行模型

---

## 第一部分：跨合约调用

### 1.1 基本跨合约调用

```rust
use rustchain_contract::{contract, storage, Address, Balance, Env, Result};

// 定义外部合约接口
#[contract_ref]
pub trait IExchange {
    fn swap(&mut self, env: &mut Env, token_in: Address, amount: Balance) -> Result<Balance>;
}

#[contract]
pub struct MyDefi {
    owner: storage::Lazy<Address>,
    exchange: storage::Lazy<Address>,
}

impl MyDefi {
    #[action]
    pub fn execute_swap(
        &mut self,
        env: &mut Env,
        token_in: Address,
        amount: Balance,
    ) -> Result<Balance> {
        // 验证调用者
        let caller = env.caller();
        let owner = self.owner.get()?;
        if caller != owner {
            return Err(rustchain_contract::Error::Unauthorized);
        }

        // 调用外部交易所合约
        let exchange_addr = self.exchange.get()?;
        let exchange = IExchange::at(exchange_addr);

        let received = exchange.swap(env, token_in, amount)?;

        env.emit_event("SwapExecuted", &[
            ("token_in", token_in),
            ("amount_in", amount),
            ("amount_out", received),
        ]);

        Ok(received)
    }
}
```

### 1.2 工厂模式

```rust
#[contract]
pub struct TokenFactory {
    token_count: storage::Lazy<u32>,
    tokens: storage::Vec<Address>,
}

impl TokenFactory {
    #[action]
    pub fn create_token(
        &mut self,
        env: &mut Env,
        name: String,
        symbol: String,
        initial_supply: Balance,
    ) -> Result<Address> {
        // 动态部署新合约
        let token_addr = env.deploy_contract(
            "my_token",
            &[name.encode(), symbol.encode(), 18u8.encode(), initial_supply.encode()],
        )?;

        let mut count = self.token_count.get()?.unwrap_or(0);
        count += 1;
        self.token_count.set(&count)?;
        self.tokens.push(&token_addr)?;

        env.emit_event("TokenCreated", &[
            ("token", token_addr),
            ("index", count),
        ]);

        Ok(token_addr)
    }

    #[view]
    pub fn get_tokens(&self) -> Result<Vec<Address>> {
        self.tokens.get_all()
    }
}
```

---

## 第二部分：自定义 Runtime 模块

### 2.1 创建 Runtime 模块

```rust
// pallets/my-module/src/lib.rs
#![cfg_attr(not(feature = "std"), no_std)]

use frame_support::{
    decl_module, decl_storage, decl_event, decl_error,
    dispatch::DispatchResult,
    traits::{Get, Currency, ReservableCurrency},
};
use frame_system::ensure_signed;

type BalanceOf<T> = <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

#[frame_support::pallet]
pub mod pallet {
    use super::*;

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type Currency: ReservableCurrency<Self::AccountId>;
        type MaxItems: Get<u32>;
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
    }

    #[pallet::storage]
    #[pallet::getter(fn items)]
    pub type Items<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        BoundedVec<u8, T::MaxItems>,
        ValueQuery,
    >;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        ItemStored(T::AccountId, Vec<u8>),
        ItemRemoved(T::AccountId),
    }

    #[pallet::error]
    pub enum Error<T> {
        ItemTooLong,
        ItemNotFound,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        #[pallet::weight(10_000)]
        pub fn store_item(origin: OriginFor<T>, item: Vec<u8>) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let bounded_item: BoundedVec<_, _> = item
                .try_into()
                .map_err(|_| Error::<T>::ItemTooLong)?;

            <Items<T>>::insert(&who, &bounded_item);
            Self::deposit_event(Event::ItemStored(who, bounded_item.into()));
            Ok(())
        }

        #[pallet::weight(5_000)]
        pub fn remove_item(origin: OriginFor<T>) -> DispatchResult {
            let who = ensure_signed(origin)?;
            ensure!(<Items<T>>::contains_key(&who), Error::<T>::ItemNotFound);
            <Items<T>>::remove(&who);
            Self::deposit_event(Event::ItemRemoved(who));
            Ok(())
        }
    }
}
```

### 2.2 集成到 Runtime

```rust
// runtime/src/lib.rs（添加模块）
impl my_module::Config for Runtime {
    type Currency = Balances;
    type MaxItems = ConstU32<256>;
    type RuntimeEvent = RuntimeEvent;
}

construct_runtime!(
    pub enum Runtime {
        // ... 其他模块
        MyModule: my_module::{Pallet, Call, Storage, Event<T>},
    }
);
```

---

## 第三部分：Gas 优化策略

### 3.1 存储优化

```rust
// ❌ 低效：多次存储读写
fn inefficient(env: &mut Env) -> Result<()> {
    let a = storage::get("key1")?;
    let b = storage::get("key2")?;
    let c = storage::get("key3")?;
    storage::set("result", &(a + b + c))?;
    Ok(())
}

// ✅ 高效：批量操作，减少存储访问
fn efficient(env: &mut Env) -> Result<()> {
    let values: Vec<u64> = storage::get_batch(&["key1", "key2", "key3"])?;
    let result: u64 = values.iter().sum();
    storage::set("result", &result)?;
    Ok(())
}
```

### 3.2 数据结构选择

```rust
// ❌ 使用 Vec 存储键值对（O(n) 查找）
pub struct BadRegistry {
    entries: storage::Vec<(Address, Balance)>,
}

// ✅ 使用 Mapping（O(1) 查找）
pub struct GoodRegistry {
    balances: storage::Mapping<Address, Balance>,
}
```

### 3.3 计算与存储权衡

```rust
// 场景：需要频繁查询总质押量

// 方案 A：每次计算（省存储，费计算）
#[view]
fn total_stake(&self) -> Result<Balance> {
    // 遍历所有质押者求和 — O(n)
    self.stakes.iter().map(|s| s.value).sum()
}

// 方案 B：缓存结果（省计算，费存储）
#[action]
fn add_stake(&mut self, env: &mut Env, amount: Balance) -> Result<()> {
    let mut total = self.cached_total.get()?.unwrap_or(0);
    total += amount;
    self.cached_total.set(&total)?;  // 多一次存储写入
    Ok(())
}

#[view]
fn total_stake(&self) -> Result<Balance> {
    self.cached_total.get()  // O(1)
}
```

> 💡 **原则：** 频繁读取的数据适合缓存；偶尔使用的数据按需计算。

---

## 第四部分：安全最佳实践

### 4.1 重入攻击防护

```rust
use rustchain_contract::ReentrancyGuard;

#[contract]
pub struct Vault {
    guard: ReentrancyGuard,
    balances: storage::Mapping<Address, Balance>,
}

impl Vault {
    #[action]
    pub fn withdraw(&mut self, env: &mut Env, amount: Balance) -> Result<()> {
        // 防重入检查
        self.guard.enter(env)?;

        let caller = env.caller();
        let balance = self.balances.get(&caller)?.unwrap_or(0);

        if balance < amount {
            self.guard.exit(env)?;
            return Err(rustchain_contract::Error::InsufficientBalance);
        }

        self.balances.insert(&caller, &(balance - amount))?;

        // 外部调用在状态更新之后
        env.transfer(&caller, amount)?;

        self.guard.exit(env)?;
        Ok(())
    }
}
```

### 4.2 整数溢出保护

```rust
// RustChain 合约框架默认使用 checked 算术
// 显式使用 safe 数学运算：

fn safe_add(a: Balance, b: Balance) -> Result<Balance> {
    a.checked_add(b)
        .ok_or(rustchain_contract::Error::ArithmeticOverflow)
}

fn safe_mul(a: Balance, b: Balance) -> Result<Balance> {
    a.checked_mul(b)
        .ok_or(rustchain_contract::Error::ArithmeticOverflow)
}
```

### 4.3 访问控制

```rust
use rustchain_contract::access::{Ownable, AccessControl};

// 角色模式
#[contract]
pub struct Governance {
    access: AccessControl,
    proposals: storage::Vec<Proposal>,
}

// 定义角色常量
const ROLE_ADMIN: &[u8] = b"ADMIN";
const ROLE_PROPOSER: &[u8] = b"PROPOSER";
const ROLE_EXECUTOR: &[u8] = b"EXECUTOR";

impl Governance {
    #[init]
    pub fn init(env: &mut Env) -> Result<Self> {
        let mut access = AccessControl::new();
        let deployer = env.caller();
        access.grant_role(env, ROLE_ADMIN, &deployer)?;
        access.grant_role(env, ROLE_PROPOSER, &deployer)?;
        access.grant_role(env, ROLE_EXECUTOR, &deployer)?;

        Ok(Self {
            access,
            proposals: storage::Vec::new(),
        })
    }

    #[action]
    pub fn create_proposal(&mut self, env: &mut Env, data: Vec<u8>) -> Result<u32> {
        self.access.ensure_role(env, ROLE_PROPOSER)?;

        let id = self.proposals.len();
        self.proposals.push(&Proposal::new(env.caller(), data))?;

        Ok(id)
    }
}
```

### 4.4 审计清单

部署前检查以下事项：

- [ ] 所有外部调用在状态更新之后（防重入）
- [ ] 使用 checked/overflow 安全算术
- [ ] 所有关键函数有访问控制
- [ ] 输入参数范围验证
- [ ] 存储大小有上限
- [ ] 没有未处理的错误路径
- [ ] Gas 消耗在合理范围内
- [ ] 通过自动化测试覆盖主要路径

---

## 第五部分：监控与运维

### 5.1 合约事件监控

```bash
# 订阅合约事件
rustchain-contract events \
  --contract rc1p4k8m2n...9qrst \
  --endpoint wss://mainnet.rustchain.org

# 或使用 JavaScript SDK
```

```javascript
// 监控合约事件示例
const { RustChain } = require('@rustchain/sdk');

const client = new RustChain('wss://mainnet.rustchain.org');
const contract = client.contract('rc1p4k8m2n...9qrst');

contract.on('Transfer', (event) => {
  console.log(`Transfer: ${event.from} → ${event.to}: ${event.value}`);
});

contract.on('SwapExecuted', (event) => {
  console.log(`Swap: ${event.amount_in} → ${event.amount_out}`);
});
```

### 5.2 Gas 监控

```bash
# 分析合约 Gas 消耗
rustchain-contract analyze \
  --wasm target/contract/my_token.wasm \
  --metrics

# 输出：
# 📊 Contract Analysis
#    Code size: 3.2 KB
#    Estimated deploy gas: 12,345,678
#    Function gas estimates:
#      init()      → ~12,000,000
#      transfer()  → ~25,000
#      balance_of()→ ~500 (view)
#      approve()   → ~20,000
```

---

## 常见问题 (FAQ)

### Q: 跨合约调用有深度限制吗？
**A:** 最大调用深度为 32 层。超过会返回 `Error::MaxCallDepthReached`。

### Q: 如何进行合约升级？
**A:** 使用 Set-Code 模式或代理模式。推荐使用代理模式，更灵活：

```rust
#[contract]
pub struct Proxy {
    implementation: storage::Lazy<Address>,
    admin: storage::Lazy<Address>,
}
```

### Q: Runtime 模块和智能合约有什么区别？
**A:**

| 特性 | Runtime 模块 | 智能合约 |
|------|-------------|----------|
| 语言 | Rust | Rust → Wasm |
| 权限 | 完全链上治理 | 受沙箱限制 |
| 升级 | 需要硬分叉/治理 | 灵活可升级 |
| 性能 | 原生速度 | Wasm 解释 |
| 适合 | 核心协议逻辑 | DApp 业务逻辑 |

### Q: 如何进行合约形式化验证？
**A:** RustChain 支持 `rustchain-verify` 工具：

```bash
cargo install rustchain-verify
rustchain-verify --contract target/contract/my_token.wasm --properties safety.props
```

### Q: 测试网和主网合约兼容吗？
**A:** 完全兼容。但注意测试网可能有不同的 Runtime 配置（如 Gas 价格、区块限制）。

---

## 下一步

🎉 恭喜完成整个 RustChain 教程系列！

你现在可以：
- 🔧 **开发 DApp** — 使用 SDK 构建去中心化应用
- 🏗️ **贡献代码** — 参与 RustChain 核心开发
- 📖 **深入学习** — 阅读 [RustChain 官方文档](https://docs.rustchain.org)
- 💬 **社区交流** — 加入 Discord 讨论技术问题

---

*本教程由 [zp6](https://github.com/zp6) 贡献至 RustChain 社区。*
