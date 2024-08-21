import requests
import subprocess
import json
import os

GITEA_URL = "https://gitea.yourdomain.com"
GITEA_TOKEN = "your_gitea_token"
GITEA_USER = "your_gitea_username"
REPO_FILE = "repos.json"

def create_gitea_repo(repo_name):
    url = f"{GITEA_URL}/api/v1/user/repos"
    headers = {"Authorization": f"token {GITEA_TOKEN}", "Content-Type": "application/json"}
    data = {"name": repo_name, "private": True}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"Repository {repo_name} created successfully on Gitea.")
    elif response.status_code == 409:
        print(f"Repository {repo_name} already exists on Gitea.")
    else:
        print(f"Failed to create repository {repo_name} on Gitea: {response.status_code}")

def mirror_repo(repo_clone_url, repo_name):
    subprocess.run(["git", "clone", "--mirror", repo_clone_url])
    os.chdir(f"{repo_name}.git")
    gitea_repo_url = f"{GITEA_URL}/{GITEA_USER}/{repo_name}.git"
    subprocess.run(["git", "remote", "add", "gitea", gitea_repo_url])
    subprocess.run(["git", "push", "--mirror", "gitea"])
    os.chdir("..")
    subprocess.run(["rm", "-rf", f"{repo_name}.git"])
    print(f"Repository {repo_name} mirrored successfully.")

def main():
    with open(REPO_FILE, "r") as f:
        repos = json.load(f)

    for repo in repos:
        repo_name = repo["name"]
        repo_clone_url = repo["clone_url"]
        create_gitea_repo(repo_name)
        mirror_repo(repo_clone_url, repo_name)

if __name__ == "__main__":
    main()
