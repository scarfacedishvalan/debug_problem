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
            ["git", "diff", f"{base_branch}...{feature_branch}"],
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


if __name__ == "__main__":
    # Example usage
    repo_path = "C:\\Python\\debug_problem"
    base_branch = "origin/main"
    feature_branch = "origin/candidate_2025-12-29"

    git_branch_diff(
        repo_path=repo_path,
        base_branch=base_branch,
        feature_branch=feature_branch,
        output_file="diff.txt",
    )
