import os
import shutil
import subprocess

def apply_solution_and_commit(solution_file, target_file, branch_name, reference_branch='main'):
    # Read solution file contents
    with open(solution_file, 'r', encoding='utf-8') as src:
        solution_code = src.read()

    # Replace target file contents
    with open(target_file, 'w', encoding='utf-8') as dst:
        dst.write(solution_code)

    # Git operations
    subprocess.run(['git', 'checkout', reference_branch], check=True)
    subprocess.run(['git', 'checkout', '-b', branch_name], check=True)
    subprocess.run(['git', 'add', target_file], check=True)
    subprocess.run(['git', 'commit', '-m', f'Apply solution from {solution_file}'], check=True)
    subprocess.run(['git', 'push', '-u', 'origin', branch_name], check=True)  # Added push
    subprocess.run(['git', 'checkout', reference_branch], check=True)


def delete_branch(branch_name, reference_branch='main'):
    subprocess.run(['git', 'checkout', reference_branch], check=True)

    subprocess.run(['git', 'branch', '-D', branch_name], check=True)
    # Delete remote branch
    subprocess.run(['git', 'push', 'origin', '--delete', branch_name], check=True)

if __name__ == "__main__":
    # Example usage:
    # Replace with actual paths if needed

    solution_files = ["sol1.py", "sol2.py", "sol3.py", "sol4.py"]
    solution_files = ["sol5.py"]
    branch_names = [f"rate_limiter_{solution_file.split('.')[0]}" for solution_file in solution_files]
    target_file = "src/rate_limiter.py"
    reference_branch = 'rate_limiter_submission'

    # for branch in branch_names:
    #     delete_branch(branch, reference_branch='rate_limiter_submission')

    for solution_file, branch_name in zip(solution_files, branch_names):
        full_solution_file = os.path.join("solutions", solution_file)
        apply_solution_and_commit(full_solution_file, target_file, branch_name, reference_branch=reference_branch)