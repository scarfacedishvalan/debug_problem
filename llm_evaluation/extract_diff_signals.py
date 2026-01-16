import json
from openai import OpenAI
from pathlib import Path
import os
# ----------------------------
# CONFIG
# ----------------------------


def pretty(obj) -> str:
    return json.dumps(obj, indent=2, sort_keys=True)

def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")

# ----------------------------
# STEP 2: BUILD PROMPT
# ----------------------------

SYSTEM_PROMPT = load_text("prompt_templates/system/diff_signals.txt")
USER_TEMPLATE = load_text("prompt_templates/user/diff_signals.txt")
DIFF_SIGNALS_SCHEMA = load_text("prompt_templates/schemas/diff_signals_schema.json")
VOCABULARY = json.loads(load_text("prompt_templates/schemas/vocabulary.json"))

def build_user_prompt(
    diff_text: str,
    diff_facts: dict    
) -> str:
    """
    Build the DiffSignals user prompt by explicit placeholder substitution.
    """

    prompt = (
        USER_TEMPLATE
        .replace("{{GIT_DIFF_TEXT}}", json.dumps(diff_text, indent=2))
        .replace("{{DIFF_FACTS}}", json.dumps(diff_facts, indent=2))
        .replace("{{VOCABULARY}}", json.dumps(VOCABULARY, indent=2))
        .replace("{{DIFF_SIGNALS_SCHEMA}}", DIFF_SIGNALS_SCHEMA)
    )

    return prompt

# ----------------------------
# STEP 3: CALL OPENAI
# ----------------------------

def evaluate_with_llm(prompt, model):
    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
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
    evaluation = response.choices[0].message.content
    return evaluation

# ----------------------------
# STEP 4: RUN PIPELINE
# ----------------------------

def gather_inputs(diff_results_dir: str):
    diff_path = os.path.join(diff_results_dir, "git_diff.txt")
    diff_text = load_text(diff_path)

    metadata_path = os.path.join(diff_results_dir, "metadata.json")

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    runner = metadata.get("runner", "git")
    timestamp = metadata.get("timestamp", "unknown")

    diff_facts_path = os.path.join(diff_results_dir, "diff_facts.json")
    with open(diff_facts_path, "r", encoding="utf-8") as f:
        diff_facts = json.load(f)

    return diff_text, diff_facts, runner, timestamp

def main(diff_results_dir: str, model: str = "gpt-4.1-mini"):
    diff_text, diff_facts, runner, timestamp = gather_inputs(diff_results_dir)
    prompt = build_user_prompt(diff_text=diff_text, diff_facts=diff_facts)

    # Save the full prompt in diff results directory for auditing
    prompt_path = os.path.join(diff_results_dir, "llm_prompt_diff_signals.txt")
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)

    evaluation = evaluate_with_llm(prompt, model)

    print("Evaluation result:")

    save_result_path = os.path.join(diff_results_dir, "diff_signals_evaluation.json")
    with open(save_result_path, "w", encoding="utf-8") as f:
        f.write(evaluation)

if __name__ == "__main__":
    REPO_PATH = "C:\Python\debug_problem"
    # Example: use latest test_results directory with git_diff.txt
    BASE_REF = "rate_limiter_submission"
    FEATURE_REF = "rate_limiter_sol4.py"
    all_dirs = os.listdir(os.path.join(REPO_PATH, "test_results"))
    all_dirs = [d for d in all_dirs if os.path.isdir(os.path.join(REPO_PATH, "test_results", d))]
    diff_results_dir = os.path.join(REPO_PATH, "test_results", all_dirs[-1])  # Use the latest test results directory
    # Or set a specific folder for testing
    diff_results_dir = r"C:\Python\testing_data\sol2\rate_limiter_sol2\run_762eb055"
    MODEL = "gpt-4.1-mini"
    main(diff_results_dir, MODEL)