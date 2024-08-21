import os
import subprocess
import requests

# Load environment variables
GITEA_URL = os.getenv('GITEA_URL')  # SSH URL
GITEA_TOKEN = os.getenv('GITEA_TOKEN')
GITEA_USER = os.getenv('GITEA_USER')  # Retained for other potential uses
GITEA_ORG = os.getenv('GITEA_ORG')    # The organization name in Gitea
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_FILE = "./all_repos.txt"

# Ensure the clone directory exists
clone_dir = "/tmp/cloned_repos"
os.makedirs(clone_dir, exist_ok=True)

def create_gitea_repo(repo_name):
    api_url = f"https://{GITEA_URL.split('@')[1]}/api/v1/orgs/{GITEA_ORG}/repos"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"token {GITEA_TOKEN}"
    }
    data = {
        "name": repo_name,
        "private": True,  # Change this to True if you want private repos
        "auto_init": False  # We don't want to initialize the repo, we'll push existing content
    }
    
    response = requests.post(api_url, headers=headers, json=data, verify=False)  # Disable SSL verification
    if response.status_code == 201:
        print(f"Repository '{repo_name}' created successfully in organization '{GITEA_ORG}'.")
    else:
        print(f"Failed to create repository '{repo_name}' in organization '{GITEA_ORG}'. Status code: {response.status_code}, Response: {response.text}")
        raise Exception(f"Failed to create repository '{repo_name}'")

def mirror_repo(repo_url):
    # Extract GitHub user/org and repo name from the URL
    url_parts = repo_url.split("/")
    github_user_org = url_parts[-2]
    repo_name = url_parts[-1].replace(".git", "")

    # Determine the Gitea repo name
    if github_user_org != GITHUB_USERNAME:
        gitea_repo_name = f"{github_user_org}-{repo_name}"
    else:
        gitea_repo_name = repo_name

    local_repo_path = os.path.join(clone_dir, repo_name)
    
    # Clone the repository with all branches and tags using GitHub credentials
    authenticated_repo_url = repo_url.replace("https://", f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@")
    subprocess.run(["git", "clone", "--mirror", authenticated_repo_url, local_repo_path], check=True)
    
    # Create the repository in the Gitea organization
    create_gitea_repo(gitea_repo_name)
    
    # Push all branches and tags to Gitea using SSH
    gitea_repo_url = f"{GITEA_URL}:{GITEA_ORG}/{gitea_repo_name}.git"
    subprocess.run(["git", "-C", local_repo_path, "push", "--mirror", gitea_repo_url], check=True)

def main():
    with open(REPO_FILE, "r") as f:
        repos = f.readlines()

    for repo in repos:
        repo = repo.strip()
        if repo:
            print(f"Mirroring repository: {repo}")
            mirror_repo(repo)
            print(f"Finished mirroring repository: {repo}")

if __name__ == "__main__":
    main()
