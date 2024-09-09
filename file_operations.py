import subprocess
import os
import logging
import shutil


def copy_files(commit_sha, clone_target_dir, changed_files, output_commit_folder, file_state):
    for file_path in changed_files:
        source_path = os.path.join(clone_target_dir, file_path)
        destination_path = os.path.join(output_commit_folder, file_state, file_path)
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        if os.path.exists(source_path):
            shutil.copy2(source_path, destination_path)
            logging.info(f"Copied {file_state} {file_path} for commit {commit_sha}")
        else:
            logging.warning(f"{file_state.capitalize()} file {file_path} not found for commit {commit_sha}")


def save_diff_patch(prev_commit_sha, commit_sha, clone_target_dir, output_commit_folder):
    diff_output_path = os.path.join(output_commit_folder, f"{commit_sha}_diff.diff")
    with open(diff_output_path, 'w') as diff_file:
        subprocess.run(["git", "diff", prev_commit_sha, commit_sha], stdout=diff_file, stderr=subprocess.STDOUT,
                       cwd=clone_target_dir)

    patch_output_path = os.path.join(output_commit_folder, f"{commit_sha}_patch.patch")
    with open(patch_output_path, 'w') as patch_file:
        subprocess.run(["git", "format-patch", f"{prev_commit_sha}..{commit_sha}", "--stdout"], stdout=patch_file,
                       stderr=subprocess.STDOUT, cwd=clone_target_dir)
