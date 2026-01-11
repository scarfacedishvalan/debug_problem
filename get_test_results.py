import subprocess
from pathlib import Path
import shutil

def run_tests_and_capture(branch: str, reference_branch, repo_path) -> Path:
    output_file = Path(f"test_results_{branch}.txt")

    # Clear .pytest_cache
    pytest_cache = Path(repo_path) / ".pytest_cache"
    if pytest_cache.exists() and pytest_cache.is_dir():
        shutil.rmtree(pytest_cache)

    subprocess.run(
        ["git", "checkout", branch],
        cwd=repo_path,
        check=True,
    )

    with output_file.open("w", encoding="utf-8") as f:
        subprocess.run(
            ["pytest"],
            stdout=f,
            cwd=repo_path,
            stderr=subprocess.STDOUT,
            check=False,   # don't crash on test failures
        )
    
    #  Commit test results artifact
    subprocess.run(
        ["git", "add", str(output_file)],
        cwd=repo_path,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", f"Add test results for {branch}"],
        cwd=repo_path,
        check=True,
    )
  

    # Checkout back to reference branch
    subprocess.run(
        ["git", "checkout", reference_branch],
        cwd=repo_path,
        check=True,
    )   

    return output_file


# Example
if __name__ == "__main__":
    REPO_PATH = "C:\\Python\\debug_problem"
    BASE_REF = "rate_limiter_submission"
    FEATURE_REF = "rate_limiter_sol4.py"
    artifact = run_tests_and_capture(FEATURE_REF, BASE_REF, REPO_PATH)
    print("Saved to:", artifact)
