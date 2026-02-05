# RustChain Network Architecture

## Overview

RustChain is a distributed ledger system designed around **Proof-of-Attestation** consensus. This document describes the network architecture, node types, and system components.

---

## High-Level Architecture

```mermaid
graph TB
    subgraph "External Layer"
        CLI[CLI Tools]
        API_CLIENTS[API Clients]
        WEB[Web Explorer]
    end
    
    subgraph "Network Layer"
        LB[Load Balancer<br/>nginx]
        PRIMARY[Primary Node<br/>50.28.86.131]
    end
    
    subgraph "Application Layer"
        API[API Server<br/>Flask/Gunicorn]
        ATTEST[Attestation Engine]
        EPOCH[Epoch Manager]
        TRANSFER[Transfer Service]
    end
    
    subgraph "Data Layer"
        LEDGER[(Ledger DB<br/>SQLite/PostgreSQL)]
        BACKUP[Backup System]
    end
    
    subgraph "Miner Network"
        M1[PowerPC G4]
        M2[PowerPC G5]
        M3[Apple Silicon]
        M4[x86_64 Modern]
    end
    
    CLI & API_CLIENTS & WEB --> LB
    LB --> PRIMARY
    PRIMARY --> API
    API --> ATTEST & EPOCH & TRANSFER
    ATTEST & EPOCH & TRANSFER --> LEDGER
    LEDGER --> BACKUP
    M1 & M2 & M3 & M4 --> |Attestations| ATTEST
```

---

## Node Architecture

### Primary Node

The primary node (`50.28.86.131`) is the central coordination point for the network.

```mermaid
graph TD
    subgraph "Primary Node"
        NGINX[nginx Reverse Proxy]
        
        subgraph "API Layer"
            GUNICORN[Gunicorn WSGI]
            FLASK[Flask Application]
        end
        
        subgraph "Core Services"
            HEALTH[Health Monitor]
            MINER_SVC[Miner Registry]
            WALLET_SVC[Wallet Service]
            EPOCH_SVC[Epoch Manager]
            ATTEST_SVC[Attestation Validator]
        end
        
        subgraph "Storage"
            DB[(SQLite DB)]
            BACKUP_DB[(Backup)]
        end
    end
    
    NGINX --> GUNICORN
    GUNICORN --> FLASK
    FLASK --> HEALTH & MINER_SVC & WALLET_SVC & EPOCH_SVC & ATTEST_SVC
    MINER_SVC & WALLET_SVC & EPOCH_SVC & ATTEST_SVC --> DB
    DB --> |Periodic| BACKUP_DB
```

### Node Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| Reverse Proxy | nginx 1.18.0 | SSL termination, load balancing |
| WSGI Server | Gunicorn | Python application serving |
| Application | Flask | API endpoints, business logic |
| Database | SQLite/PostgreSQL | Ledger storage |
| Backup | Custom | Periodic database snapshots |

---

## Miner Architecture

### Universal Miner Design

```mermaid
graph TD
    subgraph "RustChain Miner"
        MAIN[Main Loop]
        
        subgraph "Hardware Fingerprinting"
            CPU_FP[CPU Fingerprint]
            MEM_FP[Memory Fingerprint]
            DISK_FP[Disk Fingerprint]
            NET_FP[Network Fingerprint]
            ARCH_FP[Architecture Detection]
            UUID_FP[UUID Collection]
        end
        
        subgraph "Network Client"
            HTTP[HTTP Client]
            RETRY[Retry Logic]
            BACKOFF[Exponential Backoff]
        end
        
        subgraph "Cryptography"
            SIGN[Signature Generation]
            VERIFY[Response Verification]
        end
    end
    
    MAIN --> |Collect| CPU_FP & MEM_FP & DISK_FP & NET_FP & ARCH_FP & UUID_FP
    CPU_FP & MEM_FP & DISK_FP & NET_FP & ARCH_FP & UUID_FP --> SIGN
    SIGN --> HTTP
    HTTP --> RETRY
    RETRY --> |Failure| BACKOFF
```

### Miner Configuration

```python
# Example miner configuration
config = {
    "wallet_id": "my-wallet-id",
    "node_url": "https://50.28.86.131",
    "attestation_interval": 600,  # seconds
    "retry_attempts": 3,
    "backoff_base": 2,  # exponential backoff base
}
```

### Supported Platforms

| Platform | Fingerprinting Method | Notes |
|----------|----------------------|-------|
| Linux x86_64 | `/proc/cpuinfo`, `lspci`, `dmidecode` | Full support |
| Linux ARM | `/proc/cpuinfo`, device tree | Full support |
| Linux PowerPC | `/proc/cpuinfo`, device tree | Full support |
| macOS Intel | `sysctl`, `system_profiler` | Full support |
| macOS Apple Silicon | `sysctl`, `system_profiler` | Full support |
| FreeBSD | `sysctl`, `pciconf` | Partial support |

---

## Data Architecture

### Ledger Schema

```mermaid
erDiagram
    WALLETS {
        string wallet_id PK
        int64 balance
        int64 nonce
        timestamp created_at
        timestamp updated_at
    }
    
    ATTESTATIONS {
        int64 id PK
        string wallet_id FK
        json fingerprint
        float multiplier
        timestamp attested_at
        int64 epoch
    }
    
    TRANSFERS {
        int64 id PK
        string from_wallet FK
        string to_wallet FK
        int64 amount
        int64 nonce
        string signature
        timestamp created_at
    }
    
    EPOCHS {
        int64 epoch_id PK
        float pot_amount
        int64 enrolled_miners
        timestamp started_at
        timestamp ended_at
    }
    
    MINERS {
        string miner_id PK
        string hardware_type
        string device_family
        string device_arch
        float antiquity_multiplier
        timestamp last_attest
    }
    
    WALLETS ||--o{ ATTESTATIONS : has
    WALLETS ||--o{ TRANSFERS : sends
    WALLETS ||--o{ TRANSFERS : receives
    EPOCHS ||--o{ ATTESTATIONS : contains
```

### Data Flow

```mermaid
flowchart LR
    subgraph Input
        ATT[Attestation]
        TXN[Transfer]
    end
    
    subgraph Validation
        VAL_ATT[Validate Hardware]
        VAL_TXN[Validate Signature]
    end
    
    subgraph Processing
        PROC_ATT[Record Attestation]
        PROC_TXN[Execute Transfer]
    end
    
    subgraph Storage
        DB[(Database)]
    end
    
    subgraph Output
        RESPONSE[API Response]
    end
    
    ATT --> VAL_ATT --> PROC_ATT --> DB
    TXN --> VAL_TXN --> PROC_TXN --> DB
    DB --> RESPONSE
```

---

## Security Architecture

### Defense Layers

```mermaid
graph TD
    subgraph "Layer 1: Network"
        SSL[TLS 1.2+ Encryption]
        FIREWALL[Firewall Rules]
    end
    
    subgraph "Layer 2: Application"
        RATE[Rate Limiting]
        INPUT[Input Validation]
        AUTH[Authentication]
    end
    
    subgraph "Layer 3: Cryptographic"
        SIG_VERIFY[Signature Verification]
        REPLAY[Replay Protection]
        NONCE[Nonce Validation]
    end
    
    subgraph "Layer 4: Hardware"
        HW_FP[Hardware Fingerprint]
        VM_DETECT[VM Detection]
        EMU_DETECT[Emulation Detection]
    end
    
    SSL --> RATE --> SIG_VERIFY --> HW_FP
    FIREWALL --> INPUT --> REPLAY --> VM_DETECT
    AUTH --> NONCE --> EMU_DETECT
```

### Security Features (RIP-0144)

| Feature | Description | Implementation |
|---------|-------------|----------------|
| No Mock Signatures | All signatures verified | Ed25519 validation |
| Admin Key | Privileged ops require key | Header-based auth |
| Replay Protection | Nonce-based | Per-wallet counter |
| JSON Validation | Schema enforcement | Pydantic models |

---

## Network Topology

### Current Topology

```mermaid
graph TB
    subgraph "Internet"
        CLIENT1[Client 1]
        CLIENT2[Client 2]
        MINER1[Miner 1]
        MINER2[Miner 2]
    end
    
    subgraph "Edge"
        CDN[CDN/DDoS Protection]
    end
    
    subgraph "Datacenter"
        PRIMARY[Primary Node<br/>50.28.86.131]
    end
    
    CLIENT1 & CLIENT2 --> CDN
    MINER1 & MINER2 --> CDN
    CDN --> PRIMARY
```

### Future Topology (Planned)

```mermaid
graph TB
    subgraph "Internet"
        CLIENTS[Clients]
        MINERS[Miners]
    end
    
    subgraph "Edge Layer"
        CDN[CDN]
        LB[Global Load Balancer]
    end
    
    subgraph "Node Cluster"
        N1[Node US-West]
        N2[Node US-East]
        N3[Node EU]
        N4[Node Asia]
    end
    
    subgraph "Consensus Layer"
        CONSENSUS[Consensus Engine]
    end
    
    CLIENTS & MINERS --> CDN
    CDN --> LB
    LB --> N1 & N2 & N3 & N4
    N1 & N2 & N3 & N4 <--> CONSENSUS
```

---

## Deployment Architecture

### Current Deployment

```yaml
# Deployment configuration
server:
  host: 50.28.86.131
  os: Ubuntu 20.04 LTS
  cpu: 2 vCPU
  memory: 4 GB
  storage: 120 GB SSD

services:
  nginx:
    version: 1.18.0
    ports: [80, 443]
    ssl: self-signed
    
  gunicorn:
    workers: 4
    timeout: 30
    
  flask:
    version: 2.x
    debug: false
    
  database:
    type: SQLite
    backup_interval: 1h
```

### Scaling Considerations

| Metric | Current | Target |
|--------|---------|--------|
| Requests/sec | 100 | 10,000 |
| Miners | 12,000 | 100,000 |
| Database size | <1 GB | 100 GB |
| Nodes | 1 | 10+ |

---

## Monitoring Architecture

### Health Monitoring

```mermaid
graph LR
    subgraph "Monitoring"
        HEALTH[Health Endpoint]
        METRICS[Metrics Collection]
        ALERTS[Alerting]
    end
    
    subgraph "Metrics"
        UPTIME[Uptime]
        DB_STATUS[DB Status]
        TIP_AGE[Chain Tip Age]
        BACKUP_AGE[Backup Age]
    end
    
    HEALTH --> METRICS
    METRICS --> UPTIME & DB_STATUS & TIP_AGE & BACKUP_AGE
    UPTIME & DB_STATUS & TIP_AGE & BACKUP_AGE --> ALERTS
```

### Key Metrics

| Metric | Endpoint | Normal Value |
|--------|----------|--------------|
| `ok` | `/health` | `true` |
| `db_rw` | `/health` | `true` |
| `tip_age_slots` | `/health` | `< 5` |
| `backup_age_hours` | `/health` | `< 2` |
| `uptime_s` | `/health` | Increasing |

---

## Integration Points

### API Integration

```mermaid
sequenceDiagram
    participant App as External App
    participant API as RustChain API
    participant DB as Database
    
    App->>API: GET /health
    API->>App: {ok: true, ...}
    
    App->>API: GET /wallet/balance?miner_id=X
    API->>DB: SELECT balance FROM wallets
    DB->>API: balance
    API->>App: {amount_rtc: 100.5, ...}
    
    App->>API: POST /wallet/transfer/signed
    API->>API: Verify signature
    API->>DB: UPDATE balances
    DB->>API: OK
    API->>App: {success: true, tx_id: ...}
```

### Miner Integration

```mermaid
sequenceDiagram
    participant Miner
    participant API as RustChain API
    participant Validator as Attestation Validator
    participant DB as Database
    
    loop Every 10 minutes
        Miner->>Miner: Collect hardware fingerprint
        Miner->>API: POST attestation
        API->>Validator: Validate fingerprint
        Validator->>Validator: Check VM/emulation
        Validator->>Validator: Determine multiplier
        Validator->>DB: Record attestation
        DB->>API: OK
        API->>Miner: {success: true, multiplier: 2.5}
    end
```

---

## Disaster Recovery

### Backup Strategy

| Component | Frequency | Retention | Location |
|-----------|-----------|-----------|----------|
| Database | Hourly | 7 days | Local + Remote |
| Configuration | Daily | 30 days | Git repository |
| Logs | Continuous | 30 days | Log aggregator |

### Recovery Procedures

1. **Database corruption**: Restore from latest backup
2. **Node failure**: Failover to standby (planned)
3. **Network partition**: Automatic reconnection
4. **DDoS attack**: CDN mitigation

---

## Future Architecture

### Planned Improvements

1. **Multi-node consensus** — Distributed validation
2. **Geographic distribution** — Global node deployment
3. **Horizontal scaling** — Database sharding
4. **WebSocket support** — Real-time updates
5. **IPFS integration** — Decentralized storage
