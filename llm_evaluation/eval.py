import subprocess
import json
from openai import OpenAI
from pathlib import Path

# ----------------------------
# CONFIG
# ----------------------------

def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


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

SYSTEM_PROMPT = load_text("prompt_templates/system/evaluator_system.txt")
USER_TEMPLATE = load_text("prompt_templates/user/diff_evaluator_prompt.txt")

def build_user_prompt(problem_json: str, diff_text: str) -> str:
    return (
        USER_TEMPLATE
        .replace("{{PROBLEM_JSON}}", problem_json)
        .replace("{{DIFF_TEXT}}", diff_text)
    )



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
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        # response_format={"type": "json_object"},
    )
    
    raw_text = response.output_text.strip()

    try:
        evaluation = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Model returned invalid JSON:\n{raw_text}"
        ) from e

    return evaluation


# ----------------------------
# STEP 4: RUN PIPELINE
# ----------------------------

def main():
    diff_text = get_branch_diff(REPO_PATH, BASE_REF, FEATURE_REF)

    if not diff_text.strip():
        raise RuntimeError("Diff is empty — nothing to evaluate.")

    with open("problem_description.json") as f:
        problem_description_json = json.load(f)

    prompt = build_user_prompt(problem_description_json, diff_text)

    evaluation = evaluate_with_llm(prompt)

    print("Evaluation result:")
    print(json.dumps(evaluation, indent=2))


if __name__ == "__main__":
    REPO_PATH = "C:\\Python\\debug_problem"
    BASE_REF = "rate_limiter_submission"
    FEATURE_REF = "rate_limiter_sol4.py"
    MODEL = "gpt-4.1-mini"
    main()
