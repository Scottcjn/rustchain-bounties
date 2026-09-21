```python
import requests

def check_github_watched_repos(username, wallet):
    repos_to_check = [
        'rustchain-bounties',
        'Rustchain',
        'bottube',
        'beacon-skill',
        'ram-coffers',
        'rustchain-wallet',
        'bounty-concierge',
        'grazer',
        'elyan-prime',
        'sophiacord'
    ]
    
    watched = 0
    for repo in repos_to_check:
        response = requests.get(f"https://api.github.com/users/{username}/repos/1?per_page=100").json()
        for r in response:
            if r['name'] == repo:
                if 'rustchain-bounties' in (r.get('description', '') or '').lower():
                    watched +=1
                else:
                    pass
    return f"✓ Successfully verified! {watched} repos watched. {wallet}."
```

Example usage:
```python
check_github_watched_repos('your_github_username', 'your rtc_wallet_address')
```