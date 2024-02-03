import requests
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_commits(repo_owner, repo_name):
    """Fetches commits from the given GitHub repository."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"
    logging.info(f"Fetching commits for {repo_owner}/{repo_name}")
    response = requests.get(url)
    if response.status_code == 200:
        logging.info("Commits fetched successfully.")
        return response.json()
    else:
        logging.error(f"Failed to fetch commits. Status code: {response.status_code}")
        return []


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


def get_commit_diff(repo_owner, repo_name, commit_sha):
    """Fetches the diff of the specified commit."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits/{commit_sha}"
    headers = {"Accept": "application/vnd.github.v3.diff"}
    logging.info(f"Fetching diff for commit {commit_sha}")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        logging.info("Diff fetched successfully.")
        return response.text
    else:
        logging.error(f"Failed to fetch commit diff. Status code: {response.status_code}")
        return ""


def save_commit_files(folder_path, commit, diff):
    """Saves the commit message and diff to files."""
    logging.info(f"Saving files for commit {commit['sha']} in {folder_path}")
    os.makedirs(folder_path, exist_ok=True)
    with open(os.path.join(folder_path, f"{commit['sha']}_message.txt"), 'w') as message_file:
        message_file.write(commit['commit']['message'])
    with open(os.path.join(folder_path, f"{commit['sha']}_diff.diff"), 'w') as diff_file:
        diff_file.write(diff)
    logging.info(f"Files for commit {commit['sha']} saved successfully.")


def process_repositories(input_file, keywords):
    with open(input_file, 'r') as file:
        for repo_url in file:
            repo_url = repo_url.strip()
            if repo_url:
                parts = repo_url.split("/")
                repo_owner, repo_name = parts[-2], parts[-1]
                folder_path = os.path.join(os.getcwd(), repo_name)

                logging.info(f"Processing repository: {repo_name}")
                commits = get_commits(repo_owner, repo_name)
                matching_commits = search_keywords_in_commits(commits, keywords)
                for commit in matching_commits:
                    diff = get_commit_diff(repo_owner, repo_name, commit['sha'])
                    save_commit_files(folder_path, commit, diff)


def main():
    input_file = 'repositories.txt'  # Path to your input file
    keywords = ['fix', 'update']  # The keywords to search for in commit messages
    process_repositories(input_file, keywords)


if __name__ == "__main__":
    main()
