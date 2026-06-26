# rustchain-miner (RU)

Нативный майнер на Rust для [RustChain](https://github.com/Scottcjn/Rustchain) — блокчейна с доказательством древности (Proof-of-Antiquity), где старое оборудование приносит больше наград за майнинг.

## Особенности

- **Единый бинарный файл** — не требуются Python, pip или venv
- **Полный фингерпринтинг RIP-PoA** — все 6 проверок оборудования реализованы на нативном Rust
- **Встроенный ассемблер** — `rdtsc` (x86_64) / `mftb` (PowerPC) для точного измерения времени
- **Кроссплатформенность** — поддержка таргетов x86_64, aarch64, PowerPC, RISC-V (riscv64gc)
- **Самоподписанный TLS** — работает с узлом RustChain сразу после установки

## Быстрый старт

```bash
# Сборка
cargo build --release

# Запуск майнинга
./target/release/rustchain-miner --wallet ВАШ_КОШЕЛЕК

# Только проверка фингерпринтов
./target/release/rustchain-miner --test-only

# Показать полезную нагрузку аттестации (без отправки)
./target/release/rustchain-miner --wallet ВАШ_КОШЕЛЕК --show-payload

# Пробный запуск (сборка + показ полезной нагрузки, без отправки)
./target/release/rustchain-miner --wallet ВАШ_КОШЕЛЕК --dry-run

# Использование кастомного узла
./target/release/rustchain-miner --wallet ВАШ_КОШЕЛЕК --node https://your-node:port
```

## Проверки фингерпринтов RIP-PoA

| # | Проверка | Что измеряется |
|---|----------|----------------|
| 1 | Смещение часов и дрейф осциллятора | Вариация времени через `rdtsc`/`mftb` |
| 2 | Фингерпринт таймингов кэша | Свип задержек L1/L2/L3 при разных размерах буфера |
| 3 | Идентификация SIMD-блока | Тайминги инструкций SSE/AVX/AltiVec/NEON |
| 4 | Энтропия теплового дрейфа | Качество энтропии при различных тепловых состояниях |
| 5 | Джиттер пути инструкций | Цикловый джиттер в блоках целых чисел, чисел с плавающей точкой и ветвления |
| 6 | Анти-эмуляция | Обнаружение VM/гипервизора |

## Определение архитектуры

| Паттерн CPU | Семейство | Арх | Множитель |
|--------------|----------|-----|------------|
| PowerPC 7450/7447/7455 | PowerPC | g4 | 2.5x |
| PowerPC 970 | PowerPC | g5 | 2.0x |
| PowerPC 750 | PowerPC | g3 | 1.8x |
| Apple M1/M2/M3 | ARM | apple_silicon | 1.2x |
| Core 2 | x86_64 | core2duo | 1.3x |
| StarFive JH7110 | RISC-V | starfive_jh7110 | 1.1x |
| SiFive Unmatched (FU740) | RISC-V | sifive_unmatched | 1.0x |
| Milk-V Pioneer (SG2380) | RISC-V | milkv_pioneer | 0.9x |
| Generic RISC-V 64-bit | RISC-V | riscv_modern | 0.95x |
| Все остальное | x86_64 | modern | 1.0x |

## API Эндпоинты

| Эндпоинт | Метод | Описание |
|-----------|-------|-----------|
| `/health` | GET | Проверка состояния узла |
| `/epoch` | GET | Информация о текущей эпохе |
| `/attest/challenge` | POST | Запрос нонса аттестации |
| `/attest/submit` | POST | Отправка полезной нагрузки аттестации |
| `/epoch/enroll` | POST | Регистрация в текущей эпохе |
| `/wallet/balance` | GET | Проверка баланса RTC |

Узел по умолчанию: `https://50.28.86.131` (самоподписанный сертификат)

## Кросс-компиляция

```bash
# Установка cross
cargo install cross

# Сборка под разные таргеты
cross build --release --target x86_64-unknown-linux-musl
cross build --release --target aarch64-unknown-linux-musl
cross build --release --target powerpc64-unknown-linux-gnu
cross build --release --target riscv64gc-unknown-linux-gnu
```

## Запуск как службы (Linux)

Пример файла systemd юнита доступен в `contrib/rustchain-miner.service`:

```bash
# Установка бинарного файла
sudo cp target/release/rustchain-miner /usr/local/bin/

# Установка файла службы (сначала отредактируйте YOUR_USERNAME и YOUR_MINER_ID)
sudo cp contrib/rustchain-miner.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now rustchain-miner

# Проверка статуса
sudo systemctl status rustchain-miner
journalctl -u rustchain-miner -f
```

## Логирование и ротация логов

Майнер пишет логи в stderr через `env_logger`. Управляйте уровнем детализации с помощью `RUST_LOG`:

```bash
RUST_LOG=debug ./rustchain-miner --wallet my-wallet   # Детально
RUST_LOG=warn  ./rustchain-miner --wallet my-wallet   # Только предупреждения
```

При запуске в качестве службы systemd, логи попадают в journald (с автоматической ротацией). Для ручного запуска используйте перенаправление в файл с ротацией:

```bash
# Использование logrotate (создайте /etc/logrotate.d/rustchain-miner):
/var/log/rustchain-miner.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}

# Затем запускайте так:
./rustchain-miner --wallet my-wallet 2>&1 | tee -a /var/log/rustchain-miner.log
```

## TLS Сертификат

Узел по адресу `50.28.86.131` использует самоподписанный сертификат. По умолчанию майнер принимает его (аналогично `verify=False` в Python-майнере). Для повышения безопасности вы можете закрепить сертификат узла:

```bash
# Скачать сертификат узла
openssl s_client -connect 50.28.86.131:443 </dev/null 2>/dev/null | \
  openssl x509 -outform PEM > rustchain-node.pem
```

Поддержка закрепления сертификатов через флаг `--tls-cert` планируется в будущем релизе.

## Лицензия

MIT
