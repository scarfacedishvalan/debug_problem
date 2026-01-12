import subprocess
from pathlib import Path
import shutil
import os
import json
import uuid
import datetime


def run_tests_and_capture(branch: str, reference_branch: str, repo_path: str, output_dir: str) -> Path:

    # ---- evaluation run identity ----
    run_id = str(uuid.uuid4())[:8]
    timestamp = datetime.datetime.now().isoformat() + "Z"

    # eval_root = repo_path.parent / "test_results"
    # run_dir = eval_root / f"run_{run_id}"
    # run_dir.mkdir(parents=True, exist_ok=True)

    # output_file = run_dir / "pytest_output.txt"
    # metadata_file = run_dir / "metadata.json"

    # Use os instead of Path for compatibility with subprocess on Windows
    eval_root = os.path.join(repo_path, "test_results")
    run_dir = os.path.join(output_dir, branch, f"run_{run_id}")
    os.makedirs(run_dir, exist_ok=True)

    output_file = os.path.join(run_dir, "pytest_output.txt")
    metadata_file = os.path.join(run_dir, "metadata.json")

    # ---- clean pytest cache ----
    pytest_cache = os.path.join(repo_path, ".pytest_cache")
    if os.path.exists(pytest_cache) and os.path.isdir(pytest_cache):
        shutil.rmtree(pytest_cache)

    # ---- checkout candidate branch (read-only intent) ----
    subprocess.run(
        ["git", "checkout", "--quiet", branch],
        cwd=repo_path,
        check=True,
    )

    # ---- capture commit SHA ----
    commit_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_path,
        text=True,
    ).strip()

    # ---- run tests ----
    start = datetime.datetime.now()

    with open(output_file, "w", encoding="utf-8") as f:
        result = subprocess.run(
            [
                "python",
                "-m",
                "pytest",
                "tests",
                "-vv",
                "--tb=long",
                "-l",
                "--disable-warnings",
            ],
            stdout=f,
            stderr=subprocess.STDOUT,
            cwd=repo_path,
        )

    end = datetime.datetime.now()

    # ---- write structured metadata ----
    metadata = {
        "run_id": run_id,
        "timestamp": timestamp,
        "branch": branch,
        "commit_sha": commit_sha,
        "pytest_exit_code": result.returncode,
        "duration_seconds": (end - start).total_seconds(),
        "repo_path": str(repo_path),
        "output_file": str(output_file),
    }

    print("Stored test output to:", output_file)
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print("Stored metadata to:", metadata_file)

    # ---- restore reference branch ----
    subprocess.run(
        ["git", "checkout", "--quiet", reference_branch],
        cwd=repo_path,
        check=True,
    )

    return output_file


# Example usage
if __name__ == "__main__":
    REPO_PATH = "C:\\Python\\debug_problem"
    BASE_REF = "rate_limiter_submission"
    FEATURE_REF = "rate_limiter_sol1"

    artifact = run_tests_and_capture(BASE_REF, BASE_REF, REPO_PATH, output_dir=r"C:\Python\testing_data")
    print("Saved test output to:", artifact)
