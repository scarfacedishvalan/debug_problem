import subprocess
import sys
from pathlib import Path


def git_branch_diff(
    repo_path: str,
    base_branch: str,
    feature_branch: str,
    output_file: str = "diff.txt"
):
    """
    Compute diff of feature_branch against its merge-base with base_branch
    and write unified diff to a file.
    """

    try:
        diff = subprocess.check_output(
            ["git", "diff", f"{base_branch}...{feature_branch}", "--", "src/rate_limiter.py"],
            cwd=repo_path,
            text=True,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as e:
        print("Git diff failed:")
        print(e.output)
        sys.exit(1)

    Path(output_file).write_text(diff, encoding="utf-8")

    print(f"Diff written to {output_file}")
    return diff


def print_all_branches(repo_path):
    print("Local branches:")
    subprocess.run(["git", "branch"], cwd=repo_path)
    print("\nRemote branches:")
    subprocess.run(["git", "branch", "-r"], cwd=repo_path)

if __name__ == "__main__":
    # Example usage
    branches = [
        'rate_limiter_sol1',
        'rate_limiter_sol2',
        'rate_limiter_sol3',
        'rate_limiter_sol4'
    ]
    repo_path = "C:\\Python\\debug_problem"
    base_branch = "rate_limiter_submission"
    feature_branch = "rate_limiter_sol2"

    # print_all_branches(repo_path)

    filepath = r"C:\Python\testing_data\sol2\rate_limiter_sol2\run_762eb055\git_diff.txt"

    git_branch_diff(
        repo_path=repo_path,
        base_branch=base_branch,
        feature_branch=feature_branch,
        output_file=filepath,
    )
