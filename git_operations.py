import subprocess
import requests
import logging


def clone_repository(repo_url, target_dir):
    logging.info(f"Cloning repository {repo_url} into {target_dir}")
    subprocess.run(["git", "clone", repo_url, target_dir], check=True)


def checkout_commit(repo_dir, commit_sha):
    logging.info(f"Checking out to commit {commit_sha}")
    subprocess.run(["git", "-C", repo_dir, "checkout", commit_sha], check=True)


def get_previous_commit(repo_dir, commit_sha):
    result = subprocess.run(["git", "-C", repo_dir, "rev-parse", f"{commit_sha}~1"], capture_output=True, text=True)
    return result.stdout.strip()


def get_commits(repo_owner, repo_name):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"
    logging.info(f"Fetching commits for {repo_owner}/{repo_name}")
    response = requests.get(url)
    return response.json() if response.status_code == 200 else []
