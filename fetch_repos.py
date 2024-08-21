import requests
import os

GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
OUTPUT_FILE = "./all_repos.txt"

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

        for repo in data:
            repos.append(repo['clone_url'])

        page += 1

    with open(OUTPUT_FILE, "w") as f:
        for repo in repos:
            f.write(repo + "\n")
    print(f"Fetched {len(repos)} repositories.")

if __name__ == "__main__":
    fetch_repositories()
