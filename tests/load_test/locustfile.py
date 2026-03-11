from locust import HttpUser, task, between
import random
import string


class RustChainUser(HttpUser):
    """Locust user for testing RustChain API"""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts"""
        self.base_url = self.client.base_url
    
    def generate_random_data(self, length=10):
        """Generate random string for testing"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @task(20)
    def get_blocks(self):
        """Test GET /blocks endpoint"""
        self.client.get("/blocks")
    
    @task(10)
    def get_block_by_hash(self):
        """Test GET /blocks/{hash} endpoint"""
        # Generate a random hash for testing
        random_hash = self.generate_random_data(64)
        self.client.get(f"/blocks/{random_hash}")
    
    @task(20)
    def get_transactions(self):
        """Test GET /transactions endpoint"""
        self.client.get("/transactions")
    
    @task(10)
    def get_transaction_by_hash(self):
        """Test GET /transactions/{hash} endpoint"""
        # Generate a random hash for testing
        random_hash = self.generate_random_data(64)
        self.client.get(f"/transactions/{random_hash}")
    
    @task(15)
    def get_miners(self):
        """Test GET /miners endpoint"""
        self.client.get("/miners")
    
    @task(25)
    def get_stats(self):
        """Test GET /stats endpoint"""
        self.client.get("/stats")
    
    @task(5)
    def stress_test_all(self):
        """Randomly test different endpoints"""
        endpoints = [
            "/blocks",
            "/transactions",
            "/miners",
            "/stats"
        ]
        
        endpoint = random.choice(endpoints)
        self.client.get(endpoint)