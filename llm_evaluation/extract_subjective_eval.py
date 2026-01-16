import json
from openai import OpenAI
from pathlib import Path
import os

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

SYSTEM_PROMPT = load_text(
    "prompt_templates/system/subjective_eval.txt"
)

USER_TEMPLATE = load_text(
    "prompt_templates/user/subjective_eval.txt"
)

SUBJECTIVE_EVAL_SCHEMA = load_text(
    "prompt_templates/schemas/subjective_eval.json"
)

PROBLEM_CONTEXT = load_text(
    "prompt_templates/schemas/problem_context.json")
#  Load as dict for easier embedding in prompt
PROBLEM_CONTEXT = json.loads(PROBLEM_CONTEXT)


# ----------------------------
# STEP 2: BUILD USER PROMPT
# ----------------------------

def build_user_prompt(
    final_evaluation_facts: dict,
    evaluation_evidence: dict
) -> str:
    """
    Build the Subjective Evaluation user prompt.
    """

    prompt = (
        USER_TEMPLATE
        .replace(
            "{{FINAL_EVALUATION_FACTS}}",
            pretty(final_evaluation_facts)
        )
        .replace(
            "{{EVALUATION_EVIDENCE}}",
            pretty(evaluation_evidence)
        )
        .replace(
            "{{PROBLEM_CONTEXT}}",
            pretty(PROBLEM_CONTEXT)
        )
        .replace(
            "{{SUBJECTIVE_EVAL_SCHEMA}}",
            SUBJECTIVE_EVAL_SCHEMA
        )
    )

    return prompt

# ----------------------------
# STEP 3: CALL OPENAI
# ----------------------------

def evaluate_with_llm(prompt: str, model: str) -> dict:
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

    return json.loads(response.choices[0].message.content)

# ----------------------------
# STEP 4: LOAD PIPELINE INPUTS
# ----------------------------

def gather_inputs(run_dir: str):
    """
    Load deterministic artifacts and problem context.
    """

    with open(
        os.path.join(run_dir, "final_evaluation_facts.json"),
        "r",
        encoding="utf-8"
    ) as f:
        final_evaluation_facts = json.load(f)

    with open(
        os.path.join(run_dir, "evaluation_evidence.json"),
        "r",
        encoding="utf-8"
    ) as f:
        evaluation_evidence = json.load(f)

    return final_evaluation_facts, evaluation_evidence

# ----------------------------
# STEP 5: RUN PIPELINE
# ----------------------------

def main(
    run_dir: str,
    model: str = "gpt-4.1"
):
    (
        final_evaluation_facts,
        evaluation_evidence
    ) = gather_inputs(run_dir)

    prompt = build_user_prompt(
        final_evaluation_facts=final_evaluation_facts,
        evaluation_evidence=evaluation_evidence,
    )

    # Save full prompt for audit / replay
    prompt_path = os.path.join(
        run_dir,
        "llm_prompt_subjective_evaluation.txt"
    )
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)

    # -------- LLM SUBJECTIVE EVALUATION --------
    subjective_eval = evaluate_with_llm(prompt, model)

    output_path = os.path.join(
        run_dir,
        "subjective_evaluation.json"
    )
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(subjective_eval, f, indent=2)

    print("Subjective evaluation written successfully.")

# ----------------------------
# ENTRYPOINT
# ----------------------------

if __name__ == "__main__":
    RUN_DIR = r"C:\Python\testing_data\sol2\rate_limiter_sol2\run_762eb055"
    MODEL = "gpt-4.1"  # use strongest reasoning model

    main(RUN_DIR, MODEL)
