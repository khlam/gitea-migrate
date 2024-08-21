import requests
import subprocess
import os
import time

GITEA_URL = os.getenv('GITEA_URL')
GITEA_TOKEN = os.getenv('GITEA_TOKEN')
GITEA_USER = os.getenv('GITEA_USER')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_FILE = "./all_repos.txt"

def gitea_repo_exists(repo_name):
    url = f"{GITEA_URL}/api/v1/repos/{GITEA_USER}/{repo_name}"
    headers = {"Authorization": f"token {GITEA_TOKEN}"}
    response = requests.get(url, headers=headers)
    return response.status_code == 200

def create_gitea_repo(repo_name):
    if gitea_repo_exists(repo_name):
        print(f"Repository {repo_name} already exists on Gitea.")
        return False
    
    url = f"{GITEA_URL}/api/v1/user/repos"
    headers = {"Authorization": f"token {GITEA_TOKEN}", "Content-Type": "application/json"}
    data = {"name": repo_name, "private": True}
    response = requests.post(url, headers=headers, json=data)
    
    # Add a delay after Gitea interaction to be safe
    time.sleep(1)
    
    if response.status_code == 201:
        print(f"Repository {repo_name} created successfully on Gitea.")
        return True
    else:
        print(f"Failed to create repository {repo_name} on Gitea: {response.status_code}")
        return False

def mirror_repo(repo_clone_url):
    repo_name = repo_clone_url.split('/')[-1].replace('.git', '')

    if not create_gitea_repo(repo_name):
        return

    # Prepare the authenticated URL for cloning private repos
    if 'github.com' in repo_clone_url:
        repo_clone_url = repo_clone_url.replace('https://', f'https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@')

    subprocess.run(["git", "clone", "--mirror", repo_clone_url])
    
    # Add a delay between GitHub interactions
    time.sleep(1)
    
    os.chdir(f"{repo_name}.git")
    gitea_repo_url = f"{GITEA_URL}/{GITEA_USER}/{repo_name}.git"
    subprocess.run(["git", "remote", "add", "gitea", gitea_repo_url])
    subprocess.run(["git", "push", "--mirror", "gitea"])
    os.chdir("..")
    subprocess.run(["rm", "-rf", f"{repo_name}.git"])
    print(f"Repository {repo_name} mirrored successfully.")

def main():
    if not os.path.exists(REPO_FILE):
        print(f"Repository file {REPO_FILE} not found!")
        return

    with open(REPO_FILE, "r") as f:
        repos = f.read().splitlines()

    for repo in repos:
        mirror_repo(repo)

if __name__ == "__main__":
    main()
