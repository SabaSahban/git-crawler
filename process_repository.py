import os
import shutil

from git_operations import clone_repository, checkout_commit, get_previous_commit, get_commits
from file_operations import copy_files, save_diff_patch
from vulnerability_scan import run_vulnerability_scan
import logging
import subprocess


def search_keywords_in_commits(commits, keywords):
    matching_commits = []
    logging.info(f"Searching for keywords '{keywords}' in commits.")
    for commit in commits:
        if any(keyword.lower() in commit['commit']['message'].lower() for keyword in keywords):
            logging.info(f"Keyword found in commit: {commit['sha']}")
            matching_commits.append(commit)
    if not matching_commits:
        logging.warning("No keywords found in any commit.")
    return matching_commits


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
        os.makedirs(os.path.join(output_commit_folder, "original"), exist_ok=True)
        os.makedirs(os.path.join(output_commit_folder, "modified"), exist_ok=True)

        # Checkout to the previous commit to access the original state of changed files.
        checkout_commit(clone_target_dir, prev_commit_sha)
        changed_files = subprocess.check_output(["git", "diff", "--name-only", commit_sha], cwd=clone_target_dir,
                                                text=True).splitlines()
        # Copy the original state of changed files to the 'original' directory.
        copy_files(commit_sha, clone_target_dir, changed_files, output_commit_folder, "original")

        # Checkout to the target commit to access the modified state of changed files.
        checkout_commit(clone_target_dir, commit_sha)

        copy_files(commit_sha, clone_target_dir, changed_files, output_commit_folder, "modified")

        save_diff_patch(prev_commit_sha, commit_sha, clone_target_dir, output_commit_folder)

        run_vulnerability_scan(output_commit_folder)

    shutil.rmtree(clone_target_dir)


def process_repositories(input_file, keywords):
    with open(input_file, 'r') as file:
        for repo_url in file:
            repo_url = repo_url.strip()
            if repo_url:
                logging.info(f"Processing repository: {repo_url}")
                process_repository(repo_url, keywords)
