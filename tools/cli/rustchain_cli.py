import requests

def get_network_info():
    response = requests.get('https://rustchain.org/api/network')
    if response.status_code == 404:
        print("API endpoint not implemented")
    else:
        print(response.json())

def get_peers():
    response = requests.get('https://rustchain.org/api/peers')
    if response.status_code == 404:
        print("API endpoint not implemented")
    else:
        print(response.json())

def get_agents():
    response = requests.get('https://rustchain.org/api/agents')
    if response.status_code == 404:
        print("API endpoint not implemented")
    else:
        print(response.json())

def get_bounties():
    response = requests.get('https://rustchain.org/api/bounties')
    if response.status_code == 404:
        print("API endpoint not implemented")
    else:
        print(response.json())