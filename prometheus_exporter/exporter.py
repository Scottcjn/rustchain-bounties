import time
import requests
import logging
from prometheus_client import start_http_server, Gauge, Counter, Histogram, Info
from typing import Dict, Any, Optional
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RustChainPrometheusExporter:
    def __init__(self, rustchain_url: str = "http://localhost:8080", port: int = 8000, scrape_interval: int = 30):
        self.rustchain_url = rustchain_url.rstrip('/')
        self.port = port
        self.scrape_interval = scrape_interval
        
        # Node health metrics
        self.node_status = Gauge('rustchain_node_status', 'Node status (1=healthy, 0=unhealthy)')
        self.node_uptime = Gauge('rustchain_node_uptime_seconds', 'Node uptime in seconds')
        self.node_version = Info('rustchain_node_version', 'Node version information')
        self.node_peer_count = Gauge('rustchain_node_peer_count', 'Number of connected peers')
        self.node_sync_status = Gauge('rustchain_node_sync_status', 'Node sync status (1=synced, 0=syncing)')
        
        # Chain statistics
        self.chain_height = Gauge('rustchain_chain_height', 'Current blockchain height')
        self.chain_difficulty = Gauge('rustchain_chain_difficulty', 'Current mining difficulty')
        self.chain_hashrate = Gauge('rustchain_chain_hashrate', 'Current network hashrate')
        self.chain_total_supply = Gauge('rustchain_chain_total_supply', 'Total token supply')
        self.chain_circulating_supply = Gauge('rustchain_chain_circulating_supply', 'Circulating token supply')
        
        # Block metrics
        self.block_time_avg = Gauge('rustchain_block_time_avg_seconds', 'Average block time in seconds')
        self.block_size_avg = Gauge('rustchain_block_size_avg_bytes', 'Average block size in bytes')
        self.blocks_mined_total = Counter('rustchain_blocks_mined_total', 'Total blocks mined')
        self.block_transactions_avg = Gauge('rustchain_block_transactions_avg', 'Average transactions per block')
        
        # Transaction metrics
        self.mempool_size = Gauge('rustchain_mempool_size', 'Number of transactions in mempool')
        self.mempool_size_bytes = Gauge('rustchain_mempool_size_bytes', 'Size of mempool in bytes')
        self.tx_throughput = Gauge('rustchain_tx_throughput', 'Transactions per second')
        self.tx_fees_avg = Gauge('rustchain_tx_fees_avg', 'Average transaction fee')
        self.tx_confirmed_total = Counter('rustchain_tx_confirmed_total', 'Total confirmed transactions')
        
        # Miner activity metrics
        self.active_miners = Gauge('rustchain_active_miners', 'Number of active miners')
        self.mining_power_distribution = Gauge('rustchain_mining_power_distribution', 
                                              'Mining power distribution by miner', ['miner_id'])
        self.miner_rewards_total = Counter('rustchain_miner_rewards_total', 
                                          'Total rewards earned by miners', ['miner_id'])
        
        # Epoch state metrics
        self.current_epoch = Gauge('rustchain_current_epoch', 'Current epoch number')
        self.epoch_progress = Gauge('rustchain_epoch_progress', 'Epoch progress percentage (0-100)')
        self.epoch_blocks_remaining = Gauge('rustchain_epoch_blocks_remaining', 'Blocks remaining in current epoch')
        self.epoch_time_remaining = Gauge('rustchain_epoch_time_remaining_seconds', 'Estimated time remaining in epoch')
        
        # Network metrics
        self.network_bandwidth_in = Gauge('rustchain_network_bandwidth_in_bytes_per_sec', 'Incoming network bandwidth')
        self.network_bandwidth_out = Gauge('rustchain_network_bandwidth_out_bytes_per_sec', 'Outgoing network bandwidth')
        self.network_latency = Histogram('rustchain_network_latency_seconds', 'Network latency distribution')
        
        # API response time metrics
        self.api_response_time = Histogram('rustchain_api_response_time_seconds', 
                                          'API response time distribution', ['endpoint'])
        self.api_errors_total = Counter('rustchain_api_errors_total', 
                                       'Total API errors', ['endpoint', 'error_type'])

    def make_api_request(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Make API request with error handling and metrics collection"""
        url = f"{self.rustchain_url}/{endpoint.lstrip('/')}"
        start_time = time.time()
        
        try:
            response = requests.get(url, timeout=10)
            response_time = time.time() - start_time
            self.api_response_time.labels(endpoint=endpoint).observe(response_time)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.api_errors_total.labels(endpoint=endpoint, error_type='http_error').inc()
                logger.warning(f"HTTP {response.status_code} for {endpoint}")
                return None
                
        except requests.exceptions.Timeout:
            self.api_errors_total.labels(endpoint=endpoint, error_type='timeout').inc()
            logger.error(f"Timeout for {endpoint}")
            return None
        except requests.exceptions.ConnectionError:
            self.api_errors_total.labels(endpoint=endpoint, error_type='connection_error').inc()
            logger.error(f"Connection error for {endpoint}")
            return None
        except json.JSONDecodeError:
            self.api_errors_total.labels(endpoint=endpoint, error_type='json_decode_error').inc()
            logger.error(f"JSON decode error for {endpoint}")
            return None
        except Exception as e:
            self.api_errors_total.labels(endpoint=endpoint, error_type='unknown').inc()
            logger.error(f"Unknown error for {endpoint}: {str(e)}")
            return None

    def scrape_node_health(self):
        """Scrape node health metrics"""
        data = self.make_api_request('/api/node/health')
        if data:
            self.node_status.set(1 if data.get('status') == 'healthy' else 0)
            self.node_uptime.set(data.get('uptime', 0))
            self.node_peer_count.set(data.get('peer_count', 0))
            self.node_sync_status.set(1 if data.get('synced', False) else 0)
        else:
            self.node_status.set(0)

        # Get node info
        info_data = self.make_api_request('/api/node/info')
        if info_data:
            self.node_version.info({
                'version': info_data.get('version', 'unknown'),
                'build': info_data.get('build', 'unknown'),
                'commit': info_data.get('commit', 'unknown')
            })

    def scrape_chain_statistics(self):
        """Scrape blockchain statistics"""
        data = self.make_api_request('/api/chain/stats')
        if data:
            self.chain_height.set(data.get('height', 0))
            self.chain_difficulty.set(data.get('difficulty', 0))
            self.chain_hashrate.set(data.get('hashrate', 0))
            self.chain_total_supply.set(data.get('total_supply', 0))
            self.chain_circulating_supply.set(data.get('circulating_supply', 0))

    def scrape_block_metrics(self):
        """Scrape block-related metrics"""
        data = self.make_api_request('/api/blocks/stats')
        if data:
            self.block_time_avg.set(data.get('avg_block_time', 0))
            self.block_size_avg.set(data.get('avg_block_size', 0))
            self.block_transactions_avg.set(data.get('avg_transactions_per_block', 0))
            
            # Update counters (only increment by new values)
            new_blocks = data.get('total_blocks', 0)
            if hasattr(self, '_last_total_blocks'):
                blocks_diff = new_blocks - self._last_total_blocks
                if blocks_diff > 0:
                    self.blocks_mined_total._value._value += blocks_diff
            self._last_total_blocks = new_blocks

    def scrape_transaction_metrics(self):
        """Scrape transaction-related metrics"""
        mempool_data = self.make_api_request('/api/mempool')
        if mempool_data:
            self.mempool_size.set(mempool_data.get('size', 0))
            self.mempool_size_bytes.set(mempool_data.get('size_bytes', 0))

        tx_stats = self.make_api_request('/api/transactions/stats')
        if tx_stats:
            self.tx_throughput.set(tx_stats.get('tps', 0))
            self.tx_fees_avg.set(tx_stats.get('avg_fee', 0))
            
            # Update transaction counter
            new_txs = tx_stats.get('total_confirmed', 0)
            if hasattr(self, '_last_total_txs'):
                tx_diff = new_txs - self._last_total_txs
                if tx_diff > 0:
                    self.tx_confirmed_total._value._value += tx_diff
            self._last_total_txs = new_txs

    def scrape_miner_activity(self):
        """Scrape miner activity metrics"""
        data = self.make_api_request('/api/mining/stats')
        if data:
            self.active_miners.set(data.get('active_miners', 0))
            
            # Mining power distribution
            power_distribution = data.get('power_distribution', {})
            for miner_id, power in power_distribution.items():
                self.mining_power_distribution.labels(miner_id=miner_id).set(power)

        # Miner rewards
        rewards_data = self.make_api_request('/api/mining/rewards')
        if rewards_data:
            rewards = rewards_data.get('rewards', {})
            for miner_id, total_rewards in rewards.items():
                # Update rewards counter
                if not hasattr(self, '_last_miner_rewards'):
                    self._last_miner_rewards = {}
                
                last_reward = self._last_miner_rewards.get(miner_id, 0)
                reward_diff = total_rewards - last_reward
                if reward_diff > 0:
                    self.miner_rewards_total.labels(miner_id=miner_id)._value._value += reward_diff
                self._last_miner_rewards[miner_id] = total_rewards

    def scrape_epoch_state(self):
        """Scrape epoch state metrics"""
        data = self.make_api_request('/api/epoch/current')
        if data:
            self.current_epoch.set(data.get('epoch', 0))
            self.epoch_progress.set(data.get('progress_percent', 0))
            self.epoch_blocks_remaining.set(data.get('blocks_remaining', 0))
            self.epoch_time_remaining.set(data.get('time_remaining_seconds', 0))

    def scrape_network_metrics(self):
        """Scrape network metrics"""
        data = self.make_api_request('/api/network/stats')
        if data:
            self.network_bandwidth_in.set(data.get('bandwidth_in', 0))
            self.network_bandwidth_out.set(data.get('bandwidth_out', 0))
            
            # Network latency (if provided as histogram data)
            latency_data = data.get('latency_histogram', {})
            for latency, count in latency_data.items():
                for _ in range(int(count)):
                    self.network_latency.observe(float(latency))

    def scrape_all_metrics(self):
        """Scrape all metrics from RustChain node"""
        logger.info("Starting metrics scrape")
        
        try:
            self.scrape_node_health()
            self.scrape_chain_statistics()
            self.scrape_block_metrics()
            self.scrape_transaction_metrics()
            self.scrape_miner_activity()
            self.scrape_epoch_state()
            self.scrape_network_metrics()
            
            logger.info("Metrics scrape completed successfully")
        except Exception as e:
            logger.error(f"Error during metrics scrape: {str(e)}")

    def run(self):
        """Start the Prometheus exporter"""
        logger.info(f"Starting RustChain Prometheus exporter on port {self.port}")
        logger.info(f"Scraping RustChain node at {self.rustchain_url} every {self.scrape_interval} seconds")
        
        # Start Prometheus HTTP server
        start_http_server(self.port)
        
        # Main scraping loop
        while True:
            try:
                self.scrape_all_metrics()
                time.sleep(self.scrape_interval)
            except KeyboardInterrupt:
                logger.info("Exporter stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {str(e)}")
                time.sleep(self.scrape_interval)

def main():
    import os
    
    rustchain_url = os.getenv('RUSTCHAIN_URL', 'http://localhost:8080')
    port = int(os.getenv('PROMETHEUS_PORT', '8000'))
    scrape_interval = int(os.getenv('SCRAPE_INTERVAL', '30'))
    
    exporter = RustChainPrometheusExporter(
        rustchain_url=rustchain_url,
        port=port,
        scrape_interval=scrape_interval
    )
    
    exporter.run()

if __name__ == '__main__':
    main()