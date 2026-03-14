# Cross-Chain Airdrop - #1750

**任务**: RIP-305 Cross-Chain Airdrop — wRTC on Solana + Base
**价值**: 200 RTC (~$100)
**状态**: 开发中

## 架构设计

```
用户 (Solana) → 锁定 wRTC → 跨链桥 → 铸造 wRTC (Base) → 用户 (Base)
用户 (Base) → 销毁 wRTC → 跨链桥 → 解锁 wRTC (Solana) → 用户 (Solana)
```

## 核心组件

1. **Solana 合约** - Token Locker
2. **Base 合约** - Token Minter
3. **跨链桥接** - LayerZero/Wormhole 集成
4. **管理面板** - 监控和管理

## 开发计划

### Day 1 - Solana 合约
- [x] 项目结构搭建
- [ ] Token Locker 合约
- [ ] 跨链消息处理
- [ ] 单元测试

### Day 2 - Base 合约
- [ ] Token Minter 合约
- [ ] 跨链验证
- [ ] 单元测试

### Day 3 - 集成测试 + PR
- [ ] 端到端测试
- [ ] 部署文档
- [ ] 提交 PR

## 文件结构

```
1750-cross-chain-airdrop/
├── solana/
│   ├── programs/
│   │   └── locker/
│   │       ├── src/
│   │       │   └── lib.rs
│   │       └── Cargo.toml
│   └── tests/
├── base/
│   ├── contracts/
│   │   └── Minter.sol
│   └── test/
├── bridge/
│   └── config.json
└── README.md
```

---
*实时更新*
