import requests
import matplotlib.pyplot as plt
from datetime import datetime

def get_star_history(owner, repo, token=None):
    headers = {"Accept": "application/vnd.github.v3.star+json"}
    if token:
        headers["Authorization"] = f"token {token}"
        
    url = f"https://api.github.com/repos/{owner}/{repo}/stargazers"
    stars = []
    page = 1
    while True:
        r = requests.get(f"{url}?page={page}&per_page=100", headers=headers)
        if r.status_code != 200:
            break
        data = r.json()
        if not data:
            break
        for item in data:
            if 'starred_at' in item:
                stars.append(item['starred_at'])
        page += 1
        
    return stars

def plot_growth(stars, output_file="growth.png"):
    if not stars:
        print("No star data found.")
        return
    dates = [datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ") for s in stars]
    dates.sort()
    counts = list(range(1, len(dates) + 1))
    
    plt.figure(figsize=(10, 6))
    plt.plot(dates, counts, marker='o', linestyle='-')
    plt.title("GitHub Star Growth")
    plt.xlabel("Date")
    plt.ylabel("Stars")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_file)

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:
        owner, repo = sys.argv[1], sys.argv[2]
        stars = get_star_history(owner, repo)
        plot_growth(stars, f"{repo}_growth.png")
        print(f"Generated {repo}_growth.png")