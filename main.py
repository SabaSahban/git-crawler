import subprocess
import os
import logging
import shutil
import requests
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clone_repository(repo_url, target_dir):
    """Clones the repository to the target directory."""
    logging.info(f"Cloning repository {repo_url} into {target_dir}")
    subprocess.run(["git", "clone", repo_url, target_dir], check=True)

def checkout_commit(repo_dir, commit_sha):
    """Checks out the repository to the specified commit."""
    logging.info(f"Checking out to commit {commit_sha}")
    subprocess.run(["git", "-C", repo_dir, "checkout", commit_sha], check=True)

def get_previous_commit(repo_dir, commit_sha):
    """Gets the commit hash of the parent commit."""
    result = subprocess.run(["git", "-C", repo_dir, "rev-parse", f"{commit_sha}~1"], capture_output=True, text=True)
    return result.stdout.strip()

def get_commits(repo_owner, repo_name):
    """Fetches commits from the given GitHub repository."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"
    logging.info(f"Fetching commits for {repo_owner}/{repo_name}")
    response = requests.get(url)
    return response.json() if response.status_code == 200 else []

def search_keywords_in_commits(commits, keywords):
    """Searches for the keywords in commit messages and returns matching commits."""
    matching_commits = []
    logging.info(f"Searching for keywords '{keywords}' in commits.")
    for commit in commits:
        if any(keyword.lower() in commit['commit']['message'].lower() for keyword in keywords):
            logging.info(f"Keyword found in commit: {commit['sha']}")
            matching_commits.append(commit)
    if not matching_commits:
        logging.warning("No keywords found in any commit.")
    return matching_commits

def run_vulnerability_scan(scan_dir):
    """Runs a vulnerability scan on the specified directory using Semgrep."""
    logging.info(f"Running vulnerability scan on {scan_dir}")
    try:
        result = subprocess.run(["semgrep", "--config=p/r2c-security-audit", "--json", scan_dir], capture_output=True, text=True)
        if result.returncode in [0, 1]:  # Semgrep returns 1 when findings are detected
            findings = json.loads(result.stdout)
            findings_path = os.path.join(scan_dir, "semgrep_findings.json")
            with open(findings_path, 'w') as findings_file:
                json.dump(findings, findings_file, indent=4)
            logging.info(f"Vulnerability scan findings saved to {findings_path}")
        else:
            logging.error("Error running Semgrep scan.")
    except Exception as e:
        logging.error(f"Exception during Semgrep scan: {e}")

def process_repository(repo_url, keywords):
    parts = repo_url.split("/")
    repo_owner, repo_name = parts[-2], parts[-1]
    folder_path = os.path.join(os.getcwd(), "output", repo_name)

    clone_target_dir = os.path.join("clones", repo_name)
    if os.path.exists(clone_target_dir):
        shutil.rmtree(clone_target_dir)
    clone_repository(repo_url, clone_target_dir)

    commits = get_commits(repo_owner, repo_name)
    matching_commits = search_keywords_in_commits(commits, keywords)

    for commit in matching_commits:
        commit_sha = commit['sha']
        prev_commit_sha = get_previous_commit(clone_target_dir, commit_sha)

        output_commit_folder = os.path.join(folder_path, commit_sha)
        os.makedirs(output_commit_folder, exist_ok=True)

        changed_files = subprocess.check_output(["git", "diff", "--name-only", prev_commit_sha, commit_sha],
                                                cwd=clone_target_dir, text=True)
        for file_path in changed_files.splitlines():
            source_path = os.path.join(clone_target_dir, file_path)
            destination_path = os.path.join(output_commit_folder, file_path)
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            if os.path.exists(source_path):
                shutil.copy2(source_path, destination_path)
                logging.info(f"Copied {file_path} for commit {commit_sha}")

        diff_output_path = os.path.join(output_commit_folder, f"{commit_sha}_diff.diff")
        with open(diff_output_path, 'w') as diff_file:
            subprocess.run(["git", "diff", prev_commit_sha, commit_sha],
                           stdout=diff_file, stderr=subprocess.STDOUT, cwd=clone_target_dir, check=True)

        patch_output_path = os.path.join(output_commit_folder, f"{commit_sha}_patch.patch")
        with open(patch_output_path, 'w') as patch_file:
            subprocess.run(["git", "format-patch", f"{prev_commit_sha}..{commit_sha}", "--stdout"],
                           stdout=patch_file, stderr=subprocess.STDOUT, cwd=clone_target_dir, check=True)

        logging.info(f"Saved changed original files, diff, and patch for commit {commit_sha} in {output_commit_folder}")

        # Run the vulnerability scan on the saved files
        run_vulnerability_scan(output_commit_folder)

        checkout_commit(clone_target_dir, prev_commit_sha)

    shutil.rmtree(clone_target_dir)

def process_repositories(input_file, keywords):
    with open(input_file, 'r') as file:
        for repo_url in file:
            repo_url = repo_url.strip()
            if repo_url:
                logging.info(f"Processing repository: {repo_url}")
                process_repository(repo_url, keywords)

def main():
    input_file = 'repositories.txt'
    keywords = ['feat']
    process_repositories(input_file, keywords)

if __name__ == "__main__":
    main()
