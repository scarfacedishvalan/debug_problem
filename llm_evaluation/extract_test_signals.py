import subprocess
import json
from openai import OpenAI
from pathlib import Path
import os

# ----------------------------
# CONFIG
# ----------------------------

def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


# ----------------------------
# STEP 2: BUILD PROMPT
# ----------------------------

SYSTEM_PROMPT = load_text("prompt_templates/system/test_signals_user.txt")
USER_TEMPLATE = load_text("prompt_templates/user/test_signals.txt")
TEST_SIGNALS_SCHEMA = load_text("prompt_templates/schemas/test_signals_schema.json")

def build_user_prompt(test_output: str, runner: str, timestamp: str) -> str:
    return (
        USER_TEMPLATE
        .replace("{{TEST_OUTPUT_TEXT}}", test_output)
        .replace("{{RUNNER}}", runner)
        .replace("{{TIMESTAMP}}", timestamp)
        .replace("{{TEST_SIGNALS_SCHEMA}}", TEST_SIGNALS_SCHEMA)
    )



# ----------------------------
# STEP 3: CALL OPENAI
# ----------------------------

def evaluate_with_llm(prompt):
    client = OpenAI()

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        response_format={"type": "json_object"},
    )
    
    # raw_text = response.output_text.strip()


    evaluation = response.choices[0].message.content
    
    return evaluation


# ----------------------------
# STEP 4: RUN PIPELINE
# ----------------------------

def main(test_results_dir: str):
    
    test_results_path = os.path.join(test_results_dir, "pytest_output.txt")
    test_results_metadata_path = os.path.join(test_results_dir, "metadata.json")

    with open(test_results_metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    runner = metadata.get("runner", "pytest")
    timestamp = metadata.get("timestamp", "unknown")

    test_results = load_text(test_results_path)
    prompt = build_user_prompt(test_results, runner, timestamp)

    # Save the full prompt in test results directory for auditing
    prompt_path = os.path.join(test_results_dir, "llm_prompt.txt")
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)

    evaluation = evaluate_with_llm(prompt)

    print("Evaluation result:")

    save_result_path = os.path.join(test_results_dir, "test_signals_evaluation.json")

    # eval_results_str = json.dumps(evaluation, indent=2)
    with open(save_result_path, "w", encoding="utf-8") as f:
        f.write(evaluation)



if __name__ == "__main__":
    REPO_PATH = "C:\\Python\\debug_problem"
    BASE_REF = "rate_limiter_submission"
    FEATURE_REF = "rate_limiter_sol4.py"
    MODEL = "gpt-4.1-mini"
    all_dirs = os.listdir(os.path.join(REPO_PATH, "test_results"))
    all_dirs = [d for d in all_dirs if os.path.isdir(os.path.join(REPO_PATH, "test_results", d))]
    test_results_dir = os.path.join(REPO_PATH, "test_results", all_dirs[-1])  # Use the latest test results directory
    main(test_results_dir)