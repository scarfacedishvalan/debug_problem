import json
from openai import OpenAI
from pathlib import Path
import os
from eval_helpers import derive_evaluation_facts

# ----------------------------
# CONFIG / HELPERS
# ----------------------------

def pretty(obj) -> str:
    return json.dumps(obj, indent=2, sort_keys=True)

def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")

# ----------------------------
# STEP 1: LOAD PROMPTS & SCHEMA
# ----------------------------

SYSTEM_PROMPT = load_text("prompt_templates/system/evaluation_facts.txt")
USER_TEMPLATE = load_text("prompt_templates/user/evaluation_facts.txt")
EVALUATION_FACTS_SCHEMA = load_text(
    "prompt_templates/schemas/evaluation_facts.json"
)
VOCABULARY = load_text("prompt_templates/schemas/evaluation_facts_vocab.json")

# ----------------------------
# STEP 2: BUILD USER PROMPT
# ----------------------------

def build_user_prompt(
    test_signals: dict,
    diff_facts: dict,
    diff_signals: dict
) -> str:
    """
    Build the EvaluationFacts user prompt by explicit placeholder substitution.
    """

    prompt = (
        USER_TEMPLATE
        .replace("{{TEST_SIGNALS}}", pretty(test_signals))
        .replace("{{DIFF_FACTS}}", pretty(diff_facts))
        .replace("{{DIFF_SIGNALS}}", pretty(diff_signals))
        .replace("{{EVALUATION_FACTS_SCHEMA}}", EVALUATION_FACTS_SCHEMA)
        .replace("{{VOCABULARY}}", VOCABULARY)
    )

    return prompt

# ----------------------------
# STEP 3: CALL OPENAI
# ----------------------------

def evaluate_with_llm(prompt: str, model: str) -> str:
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
                "content": prompt
            }
        ],
        response_format={"type": "json_object"},
    )

    return response.choices[0].message.content

# ----------------------------
# STEP 4: LOAD PIPELINE INPUTS
# ----------------------------

def gather_inputs(run_dir: str):
    """
    Load structured artifacts produced by previous pipeline stages.
    """

    with open(os.path.join(run_dir, "test_signals_evaluation.json"), "r", encoding="utf-8") as f:
        test_signals = json.load(f)

    with open(os.path.join(run_dir, "diff_facts.json"), "r", encoding="utf-8") as f:
        diff_facts = json.load(f)

    with open(os.path.join(run_dir, "diff_signals_evaluation.json"), "r", encoding="utf-8") as f:
        diff_signals = json.load(f)

    return test_signals, diff_facts, diff_signals

# ----------------------------
# STEP 5: RUN PIPELINE
# ----------------------------

def main(run_dir: str, model: str = "gpt-4.1-mini"):
    test_signals, diff_facts, diff_signals = gather_inputs(run_dir)

    prompt = build_user_prompt(
        test_signals=test_signals,
        diff_facts=diff_facts,
        diff_signals=diff_signals
    )

    # Save prompt for audit / replay
    prompt_path = os.path.join(run_dir, "llm_prompt_evaluation_facts.txt")
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)

    # -------- LLM EVIDENCE --------
    evaluation_evidence_raw = evaluate_with_llm(prompt, model)
    evaluation_evidence = json.loads(evaluation_evidence_raw)

    evidence_path = os.path.join(run_dir, "evaluation_evidence.json")
    with open(evidence_path, "w", encoding="utf-8") as f:
        json.dump(evaluation_evidence, f, indent=2)

    # -------- DETERMINISTIC DERIVATION --------
    final_evaluation = derive_evaluation_facts(evaluation_evidence)

    final_path = os.path.join(run_dir, "final_evaluation_facts.json")
    with open(final_path, "w", encoding="utf-8") as f:
        json.dump(final_evaluation, f, indent=2)

    print("Final EvaluationFacts derived successfully.")


# ----------------------------
# ENTRYPOINT
# ----------------------------

if __name__ == "__main__":
    REPO_PATH = r"C:\Python\debug_problem"

    # Example: select a specific run directory
    RUN_DIR = r"C:\Python\testing_data\sol2\rate_limiter_sol2\run_762eb055"

    MODEL = "gpt-4.1-mini"

    main(RUN_DIR, MODEL)
