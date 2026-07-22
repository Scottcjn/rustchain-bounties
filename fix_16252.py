import logging
import time
import random

class HeaderRetryPolicy:
    def __init__(self, max_retries=5, backoff_factor=2):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.rejected_headers = {}

    def should_retry(self, header, rejection_reason):
        if rejection_reason['retryable']:
            return True
        elif header in self.rejected_headers:
            return False
        else:
            self.rejected_headers[header] = True
            return False

    def get_backoff_time(self, retry_count):
        return min(2 ** (retry_count * self.backoff_factor), 300)  # cap at 5 minutes

def submit_header(header, node):
    retry_policy = HeaderRetryPolicy()
    retry_count = 0
    while True:
        response = node.submit_header(header)
        if response['accepted']:
            return
        elif retry_policy.should_retry(header, response['rejection_reason']):
            logging.warning(f"Header rejected: {response['rejection_reason']}")
            backoff_time = retry_policy.get_backoff_time(retry_count)
            logging.info(f"Retrying in {backoff_time} seconds...")
            time.sleep(backoff_time)
            retry_count += 1
            if retry_count >= retry_policy.max_retries:
                logging.error(f"Max retries exceeded for header: {header}")
                break
        else:
            logging.error(f"Non-retryable rejection reason: {response['rejection_reason']}")
            break

class Node:
    def __init__(self, url):
        self.url = url

    def submit_header(self, header):
        # simulate node submission
        import requests
        response = requests.post(self.url, json=header)
        if response.status_code == 200:
            return {'accepted': True}
        else:
            return {'accepted': False, 'rejection_reason': {'retryable': False, 'message': response.text}}

class WindowsHeadlessMiner:
    def __init__(self, node):
        self.node = node

    def run(self):
        while True:
            header = self.generate_header()
            submit_header(header, self.node)

    def generate_header(self):
        # simulate header generation
        return {'block_number': 1, 'transactions': []}

if __name__ == '__main__':
    node = Node('https://example.com/submit_header')
    miner = WindowsHeadlessMiner(node)
    miner.run()