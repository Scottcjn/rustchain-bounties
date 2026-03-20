#!/usr/bin/env python3
"""
Multi-Node Health Dashboard for RustChain Attestation Nodes
Monitors all 3 attestation nodes and provides a comprehensive health dashboard.
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Optional

class HealthChecker:
    def __init__(self, node_urls: List[str]):
        self.node_urls = node_urls
        self.results = {}
        self.timeout = 10  # seconds
        
    def check_node_health(self, node_url: str) -> Dict:
        """Check health of a single node"""
        health_info = {
            'url': node_url,
            'timestamp': datetime.now().isoformat(),
            'status': 'unknown',
            'response_time': None,
            'error': None,
            'details': {}
        }
        
        try:
            start_time = time.time()
            response = requests.get(
                f"{node_url}/health", 
                timeout=self.timeout,
                headers={'Accept': 'application/json'}
            )
            end_time = time.time()
            
            health_info['response_time'] = round((end_time - start_time) * 1000, 2)  # ms
            
            if response.status_code == 200:
                health_info['status'] = 'healthy'
                health_info['details'] = response.json()
            else:
                health_info['status'] = 'unhealthy'
                health_info['error'] = f"HTTP {response.status_code}: {response.text}"
                
        except requests.exceptions.Timeout:
            health_info['status'] = 'timeout'
            health_info['error'] = 'Request timed out'
        except requests.exceptions.ConnectionError:
            health_info['status'] = 'connection_error'
            health_info['error'] = 'Failed to connect to node'
        except Exception as e:
            health_info['status'] = 'error'
            health_info['error'] = str(e)
            
        return health_info
    
    def check_all_nodes(self) -> Dict:
        """Check health of all nodes"""
        self.results = {}
        
        for i, node_url in enumerate(self.node_urls):
            print(f"Checking node {i+1}/{len(self.node_urls)}: {node_url}")
            self.results[f"node_{i+1}"] = self.check_node_health(node_url)
            
        return self.results
    
    def generate_dashboard(self) -> str:
        """Generate a health dashboard report"""
        if not self.results:
            return "No health data available. Run check_all_nodes() first."
            
        dashboard = "\n" + "="*80 + "\n"
        dashboard += "RUSTCHAIN MULTI-NODE HEALTH DASHBOARD\n"
        dashboard += "="*80 + "\n\n"
        dashboard += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Overall status
        healthy_nodes = sum(1 for result in self.results.values() if result['status'] == 'healthy')
        total_nodes = len(self.results)
        
        dashboard += f"OVERALL STATUS: {healthy_nodes}/{total_nodes} nodes healthy\n\n"
        
        # Individual node details
        for node_name, node_data in self.results.items():
            dashboard += f"{node_name.upper()} ({node_data['url']})\n"
            dashboard += f"  Status: {node_data['status'].upper()}\n"
            
            if node_data['response_time'] is not None:
                dashboard += f"  Response Time: {node_data['response_time']}ms\n"
                
            if node_data['error']:
                dashboard += f"  Error: {node_data['error']}\n"
                
            if node_data['details']:
                dashboard += "  Details:\n"
                for key, value in node_data['details'].items():
                    dashboard += f"    {key}: {value}\n"
                    
            dashboard += "\n"
        
        # Recommendations
        dashboard += "RECOMMENDATIONS:\n"
        if healthy_nodes < total_nodes:
            dashboard += f"⚠️  {total_nodes - healthy_nodes} node(s) need attention\n"
        else:
            dashboard += "✅ All nodes are healthy\n"
            
        # Performance metrics
        response_times = [r['response_time'] for r in self.results.values() if r['response_time'] is not None]
        if response_times:
            avg_response = sum(response_times) / len(response_times)
            max_response = max(response_times)
            min_response = min(response_times)
            
            dashboard += f"\nPERFORMANCE METRICS:\n"
            dashboard += f"  Average Response Time: {avg_response:.2f}ms\n"
            dashboard += f"  Max Response Time: {max_response:.2f}ms\n"
            dashboard += f"  Min Response Time: {min_response:.2f}ms\n"
            
        dashboard += "="*80 + "\n"
        return dashboard
    
    def save_results(self, filename: str = "health_check_results.json"):
        """Save health check results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"Results saved to {filename}")

def main():
    # Default node URLs - should be updated with actual node URLs
    default_nodes = [
        "https://node1.rustchain.com",
        "https://node2.rustchain.com", 
        "https://node3.rustchain.com"
    ]
    
    # Allow custom node URLs as command line arguments
    if len(sys.argv) > 1:
        node_urls = sys.argv[1:]
    else:
        node_urls = default_nodes
        print(f"Using default nodes: {node_urls}")
        print("To specify custom nodes, pass them as arguments:")
        print("  python health-check.py https://node1.url https://node2.url https://node3.url")
    
    checker = HealthChecker(node_urls)
    
    try:
        print("Starting health check...")
        results = checker.check_all_nodes()
        
        # Display dashboard
        dashboard = checker.generate_dashboard()
        print(dashboard)
        
        # Save results
        checker.save_results()
        
        # Exit with appropriate code
        healthy_count = sum(1 for r in results.values() if r['status'] == 'healthy')
        sys.exit(0 if healthy_count == len(node_urls) else 1)
        
    except KeyboardInterrupt:
        print("\nHealth check interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error during health check: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
