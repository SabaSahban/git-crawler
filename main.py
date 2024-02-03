import requests


def get_commits(repo_owner, repo_name):
    """Fetches commits from the given GitHub repository."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch commits.")
        return []


def search_keyword_in_commits(commits, keyword):
    """Searches for the keyword in commit messages."""
    for commit in commits:
        if keyword.lower() in commit['commit']['message'].lower():
            return commit
    return None


def get_commit_diff(repo_owner, repo_name, commit_sha):
    """Fetches the diff of the specified commit."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits/{commit_sha}"
    headers = {"Accept": "application/vnd.github.v3.diff"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print("Failed to fetch commit diff.")
        return ""


def main(repo_url, keyword):
    # Extract repository owner and name from URL
    parts = repo_url.split("/")
    repo_owner, repo_name = parts[-2], parts[-1]

    commits = get_commits(repo_owner, repo_name)
    commit = search_keyword_in_commits(commits, keyword)
    if commit:
        print(f"Keyword '{keyword}' found in commit: {commit['sha']}")
        diff = get_commit_diff(repo_owner, repo_name, commit['sha'])
        print(diff)
    else:
        print(f"Keyword '{keyword}' not found in any commit.")


# Example usage
repo_url = 'https://github.com/example_user/example_repo'
keyword = 'fix'
main(repo_url, keyword)
