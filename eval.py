import subprocess
import json
from openai import OpenAI

# ----------------------------
# CONFIG
# ----------------------------

REPO_PATH = "C:\\Python\\debug_problem"
BASE_REF = "origin/main"
FEATURE_REF = "origin/candidate_2025-12-29"
MODEL = "gpt-4.1-mini"

PROBLEM_DESCRIPTION = """
The function `factorial(n)` is intended to compute n! recursively.
The known bug is that the base case for n == 0 is incorrect.
The function currently returns 0 for n == 0, but mathematically 0! = 1.
"""

# ----------------------------
# STEP 1: GET BRANCH DIFF
# ----------------------------

def get_branch_diff(repo_path, base_ref, feature_ref):
    subprocess.check_call(
        ["git", "fetch", "--all", "--prune"],
        cwd=repo_path,
    )

    diff = subprocess.check_output(
        ["git", "diff", f"{base_ref}...{feature_ref}"],
        cwd=repo_path,
        text=True,
    )

    return diff


# ----------------------------
# STEP 2: BUILD PROMPT
# ----------------------------

def build_prompt(problem_description, diff_text):
    return f"""
Problem description:
{problem_description.strip()}

Here is the code change (unified diff):

{diff_text}

Evaluate the change and answer ONLY in JSON using this schema:

{{
  "fixes_root_cause": boolean,
  "change_scope": "minimal" | "moderate" | "excessive",
  "introduces_unrelated_changes": boolean
}}
"""


# ----------------------------
# STEP 3: CALL OPENAI
# ----------------------------

def evaluate_with_llm(prompt):
    client = OpenAI()

    response = client.responses.create(
        model=MODEL,
        input=[
            {
                "role": "system",
                "content": (
                    "You are an automated code evaluation assistant. "
                    "Evaluate whether a proposed code change correctly fixes the stated bug. "
                    "Do not speculate about tests or runtime behavior. "
                    "Respond ONLY with valid JSON."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        # response_format={"type": "json_object"},
    )
    evaluation = json.loads(response.output_text)


    return evaluation


# ----------------------------
# STEP 4: RUN PIPELINE
# ----------------------------

def main():
    diff_text = get_branch_diff(REPO_PATH, BASE_REF, FEATURE_REF)

    if not diff_text.strip():
        raise RuntimeError("Diff is empty — nothing to evaluate.")

    prompt = build_prompt(PROBLEM_DESCRIPTION, diff_text)

    evaluation = evaluate_with_llm(prompt)

    print("Evaluation result:")
    print(json.dumps(evaluation, indent=2))


if __name__ == "__main__":
    main()
