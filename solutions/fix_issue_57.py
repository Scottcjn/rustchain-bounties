import requests
import itertools
import json
from requests.exceptions import RequestException

class APISecurityTester:
    def __init__(self, base_url, endpoints, common_passwords, headers=None):
        self.base_url = base_url
        self.endpoints = endpoints
        self.common_passwords = common_passwords
        self.headers = headers if headers else {}

    def brute_force_admin_key(self):
        for endpoint in self.endpoints:
            for password in self.common_passwords:
                try:
                    response = requests.post(
                        f"{self.base_url}/{endpoint}",
                        headers=self.headers,
                        data={'admin_key': password}
                    )
                    if response.status_code == 200:
                        print(f"Vulnerability found at {endpoint} with password: {password}")
                except RequestException as e:
                    print(f"Request failed: {e}")

    def rate_limit_bypass(self):
        for endpoint in self.endpoints:
            try:
                for ip in self.generate_ip_addresses():
                    headers = self.headers.copy()
                    headers['X-Forwarded-For'] = ip
                    response = requests.get(f"{self.base_url}/{endpoint}", headers=headers)
                    print(f"Response from {endpoint} with IP {ip}: {response.status_code}")
            except RequestException as e:
                print(f"Request failed: {e}")

    def authentication_bypass(self):
        for endpoint in self.endpoints:
            try:
                response = requests.get(f"{self.base_url}/{endpoint}")
                if response.status_code == 200:
                    print(f"Authentication bypass possible at {endpoint}")
            except RequestException as e:
                print(f"Request failed: {e}")

    def header_injection(self):
        for endpoint in self.endpoints:
            try:
                headers = self.headers.copy()
                headers['X-Forwarded-For'] = '127.0.0.1\r\nX-Injected-Header: malicious'
                response = requests.get(f"{self.base_url}/{endpoint}", headers=headers)
                print(f"Header injection test at {endpoint}: {response.status_code}")
            except RequestException as e:
                print(f"Request failed: {e}")

    def parameter_pollution(self):
        for endpoint in self.endpoints:
            try:
                response = requests.get(f"{self.base_url}/{endpoint}?param=value&param=malicious")
                print(f"Parameter pollution test at {endpoint}: {response.status_code}")
            except RequestException as e:
                print(f"Request failed: {e}")

    def generate_ip_addresses(self):
        # Generate a list of IP addresses for testing
        return ['192.168.1.1', '192.168.1.2', '192.168.1.3']

    def run_tests(self):
        self.brute_force_admin_key()
        self.rate_limit_bypass()
        self.authentication_bypass()
        self.header_injection()
        self.parameter_pollution()

if __name__ == "__main__":
    base_url = "http://example.com/api"
    endpoints = ["admin", "user", "data"]
    common_passwords = ["admin", "password", "123456"]
    tester = APISecurityTester(base_url, endpoints, common_passwords)
    tester.run_tests()