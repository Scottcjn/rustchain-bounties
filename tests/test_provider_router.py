#!/usr/bin/env python3
"""Tests for Provider Router"""

import pytest
import time
from pathlib import Path
from unittest.mock import patch, Mock

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from provider_router.router import (
    ProviderRouter,
    Provider,
    ProviderConfig,
    ProviderMetrics,
    ProviderStatus,
    RateLimiter,
    create_router,
)


class TestProviderConfig:
    """Test ProviderConfig dataclass"""

    def test_default_config(self):
        config = ProviderConfig(name="test")
        assert config.name == "test"
        assert config.max_requests_per_minute == 60
        assert config.enabled is True
        assert config.priority == 100

    def test_custom_config(self):
        config = ProviderConfig(
            name="custom",
            api_key="secret123",
            max_requests_per_minute=100,
            priority=10,
            enabled=False,
        )
        assert config.name == "custom"
        assert config.api_key == "secret123"
        assert config.priority == 10
        assert config.enabled is False


class TestProviderMetrics:
    """Test ProviderMetrics dataclass"""

    def test_empty_metrics(self):
        metrics = ProviderMetrics()
        assert metrics.total_requests == 0
        assert metrics.success_rate == 0.0
        assert metrics.average_latency_ms == 0.0

    def test_success_rate_calculation(self):
        metrics = ProviderMetrics()
        metrics.total_requests = 10
        metrics.successful_requests = 8
        assert metrics.success_rate == 0.8

    def test_average_latency(self):
        metrics = ProviderMetrics()
        metrics.total_requests = 5
        metrics.total_latency_ms = 500.0
        assert metrics.average_latency_ms == 100.0


class TestProvider:
    """Test Provider class"""

    def test_create_provider(self):
        config = ProviderConfig(name="test")
        provider = Provider(config)
        
        assert provider.config.name == "test"
        assert provider.status == ProviderStatus.UNKNOWN
        assert provider.metrics.total_requests == 0

    def test_is_available(self):
        config = ProviderConfig(name="test", enabled=True)
        provider = Provider(config, status=ProviderStatus.HEALTHY)
        
        assert provider.is_available() is True

    def test_is_not_available_when_disabled(self):
        config = ProviderConfig(name="test", enabled=False)
        provider = Provider(config, status=ProviderStatus.HEALTHY)
        
        assert provider.is_available() is False

    def test_is_not_available_when_down(self):
        config = ProviderConfig(name="test", enabled=True)
        provider = Provider(config, status=ProviderStatus.DOWN)
        
        assert provider.is_available() is False


class TestRateLimiter:
    """Test RateLimiter class"""

    def test_acquire_within_limit(self):
        limiter = RateLimiter(max_requests_per_minute=5)
        
        for _ in range(5):
            assert limiter.acquire() is True

    def test_acquire_exceeds_limit(self):
        limiter = RateLimiter(max_requests_per_minute=2)
        
        limiter.acquire()
        limiter.acquire()
        
        assert limiter.acquire() is False

    def test_rate_limit_resets(self):
        limiter = RateLimiter(max_requests_per_minute=1)
        
        assert limiter.acquire() is True
        assert limiter.acquire() is False


class TestProviderRouter:
    """Test ProviderRouter class"""

    def test_create_router(self):
        router = ProviderRouter()
        providers = router.get_all_providers()
        
        assert len(providers) >= 4  # Default providers

    def test_add_provider(self):
        router = ProviderRouter()
        config = ProviderConfig(name="custom", priority=5)
        router.add_provider(config)
        
        provider = router.get_provider("custom")
        assert provider is not None
        assert provider.config.name == "custom"

    def test_remove_provider(self):
        router = ProviderRouter()
        router.add_provider(ProviderConfig(name="temp"))
        
        assert router.remove_provider("temp") is True
        assert router.get_provider("temp") is None

    def test_get_provider_by_name(self):
        router = ProviderRouter()
        
        provider = router.get_provider("grok")
        assert provider is not None
        assert provider.config.name == "grok"

    def test_select_provider(self):
        router = ProviderRouter()
        
        provider = router.select_provider()
        assert provider is not None

    def test_select_with_requirements(self):
        router = ProviderRouter()
        
        # Provider with good success rate
        provider = router.get_provider("grok")
        provider.metrics.total_requests = 10
        provider.metrics.successful_requests = 10
        
        selected = router.select_provider({"min_success_rate": 0.9})
        assert selected is not None

    def test_select_no_match(self):
        router = ProviderRouter()
        
        # All providers will fail this requirement
        selected = router.select_provider({"min_success_rate": 1.0})  # 100% required
        assert selected is None

    def test_record_request_success(self):
        router = ProviderRouter()
        
        router.record_request("grok", True, 100.0)
        
        metrics = router.get_metrics("grok")
        assert metrics.total_requests == 1
        assert metrics.successful_requests == 1

    def test_record_request_failure(self):
        router = ProviderRouter()
        
        router.record_request("grok", False, 100.0)
        
        metrics = router.get_metrics("grok")
        assert metrics.total_requests == 1
        assert metrics.failed_requests == 1

    def test_update_provider_status(self):
        router = ProviderRouter()
        
        router.update_provider_status("grok", ProviderStatus.HEALTHY)
        
        provider = router.get_provider("grok")
        assert provider.status == ProviderStatus.HEALTHY

    def test_fallback_on_failure(self):
        router = ProviderRouter()
        
        # Mark Grok as down
        router.update_provider_status("grok", ProviderStatus.DOWN)
        
        # Should still get a provider
        provider = router.select_provider()
        assert provider is not None
        assert provider.config.name != "grok"

    def test_execute_request_success(self):
        router = ProviderRouter()
        
        result = router.execute_request("test prompt")
        
        assert result["success"] is True
        assert "provider" in result
        assert "result" in result

    def test_get_healthy_providers(self):
        router = ProviderRouter()
        
        # Set one as healthy
        router.update_provider_status("grok", ProviderStatus.HEALTHY)
        
        healthy = router.get()
        assert len_healthy_providers(healthy) >= 1


class TestCreateRouter:
    """Test create_router convenience function"""

    def test_create_with_keys(self):
        router = create_router(
            grok_key="test-key",
            openai_key="test-key",
        )
        
        providers = router.get_all_providers()
        names = [p.config.name for p in providers]
        
        assert "grok" in names
        assert "openai" in names

    def test_create_empty(self):
        router = create_router()  # No keys
        
        # Should still have default providers
        providers = router.get_all_providers()
        assert len(providers) >= 4


class TestIntegration:
    """Integration tests"""

    def test_full_workflow(self):
        router = ProviderRouter()
        
        # Add custom provider
        router.add_provider(ProviderConfig(
            name="test-provider",
            priority=1,  # Highest priority
        ))
        
        # Select should return highest priority
        provider = router.select_provider()
        assert provider.config.name == "test-provider"
        
        # Make request
        result = router.execute_request("test")
        assert result["success"] is True
        
        # Check metrics
        metrics = router.get_all_metrics()
        assert len(metrics) > 0

    def test_rate_limiting(self):
        router = ProviderRouter()
        
        # Exhaust rate limit
        limiter = router._rate_limiters["grok"]
        for _ in range(60):
            limiter.acquire()
        
        # Should not get grok
        provider = router.select_provider()
        assert provider.config.name != "grok"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
