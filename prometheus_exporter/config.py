import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PrometheusConfig:
    """Configuration for Prometheus exporter"""
    listen_host: str = "0.0.0.0"
    listen_port: int = 8000
    metrics_path: str = "/metrics"
    scrape_interval: int = 30  # seconds
    scrape_timeout: int = 10   # seconds


@dataclass
class NodeConfig:
    """Configuration for Radix node connection"""
    node_url: str = "https://mainnet.radixdlt.com"
    api_timeout: int = 30      # seconds
    retry_attempts: int = 3
    retry_delay: int = 5       # seconds


@dataclass
class Config:
    """Main configuration class"""
    prometheus: PrometheusConfig
    node: NodeConfig
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables"""
        prometheus_config = PrometheusConfig(
            listen_host=os.getenv("PROMETHEUS_HOST", "0.0.0.0"),
            listen_port=int(os.getenv("PROMETHEUS_PORT", "8000")),
            metrics_path=os.getenv("PROMETHEUS_METRICS_PATH", "/metrics"),
            scrape_interval=int(os.getenv("PROMETHEUS_SCRAPE_INTERVAL", "30")),
            scrape_timeout=int(os.getenv("PROMETHEUS_SCRAPE_TIMEOUT", "10"))
        )
        
        node_config = NodeConfig(
            node_url=os.getenv("RADIX_NODE_URL", "https://mainnet.radixdlt.com"),
            api_timeout=int(os.getenv("RADIX_API_TIMEOUT", "30")),
            retry_attempts=int(os.getenv("RADIX_RETRY_ATTEMPTS", "3")),
            retry_delay=int(os.getenv("RADIX_RETRY_DELAY", "5"))
        )
        
        return cls(
            prometheus=prometheus_config,
            node=node_config,
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )
    
    def validate(self) -> bool:
        """Validate configuration values"""
        if self.prometheus.listen_port < 1 or self.prometheus.listen_port > 65535:
            raise ValueError(f"Invalid port: {self.prometheus.listen_port}")
        
        if self.prometheus.scrape_interval < 1:
            raise ValueError(f"Scrape interval must be positive: {self.prometheus.scrape_interval}")
        
        if self.prometheus.scrape_timeout < 1:
            raise ValueError(f"Scrape timeout must be positive: {self.prometheus.scrape_timeout}")
        
        if self.node.api_timeout < 1:
            raise ValueError(f"API timeout must be positive: {self.node.api_timeout}")
        
        if self.node.retry_attempts < 0:
            raise ValueError(f"Retry attempts must be non-negative: {self.node.retry_attempts}")
        
        if self.node.retry_delay < 0:
            raise ValueError(f"Retry delay must be non-negative: {self.node.retry_delay}")
        
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            raise ValueError(f"Invalid log level: {self.log_level}")
        
        return True
    
    def setup_logging(self) -> None:
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


# Global configuration instance
config = Config.from_env()