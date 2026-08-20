import pytest
from typing import Dict, Any

# Добавленные зависимости для CI тестов
pytest_plugins = [
    "tests.test_rtc_reward_action",
    "tests.test_wallet_action",
]

# Тестовые зависимости
test_dependencies = {
    "aiohttp": ">=3.8.1",
    "flask-cors": ">=3.0.10",
    "matplotlib": ">=3.5.1",
    "seaborn": ">=0.11.2",
    "pytest": ">=7.0.0",
    "pytest-asyncio": ">=0.18.1",
}

def pytest_configure(config: Any) -> None:
    config.option.test_dependencies = test_dependencies