import requests
import json

GITHUB_USERNAME = "your_github_username"
GITHUB_TOKEN = "your_github_token"
OUTPUT_FILE = "repos.json"

def fetch_repositories():
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/user/repos?per_page=100&page={page}"
        response = requests.get(url, auth=(GITHUB_USERNAME, GITHUB_TOKEN))
        if response.status_code != 200:
            print(f"Error fetching repositories: {response.status_code}")
            break

        data = response.json()
        if not data:
            break

        repos.extend(data)
        page += 1

    with open(OUTPUT_FILE, "w") as f:
        json.dump(repos, f, indent=4)
    print(f"Fetched {len(repos)} repositories.")

if __name__ == "__main__":
    fetch_repositories()
