import re
from collections import defaultdict
from unidiff import PatchSet
import os

DEF_RE = re.compile(r'^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(')
CLASS_RE = re.compile(r'^\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)')

def extract_diff_facts(diff_text: str):
    files = {}
    current_file = None
    current_func = None
    current_class = None

    files_changed = 0
    total_added = 0
    total_removed = 0
    test_files_changed = False

    for line in diff_text.splitlines():
        # New file block
        if line.startswith("diff --git"):
            parts = line.split(" ")
            path = parts[-1][2:]  # remove b/
            current_file = path
            files_changed += 1

            files[current_file] = {
                "lines_added": 0,
                "lines_removed": 0,
                "functions_touched": set(),
                "classes_touched": set()
            }

            if "test" in current_file.lower():
                test_files_changed = True

            current_func = None
            current_class = None
            continue

        if current_file is None:
            continue

        # Track context
        class_match = CLASS_RE.match(line)
        if class_match:
            current_class = class_match.group(1)
            files[current_file]["classes_touched"].add(current_class)

        func_match = DEF_RE.match(line)
        if func_match:
            current_func = func_match.group(1)
            files[current_file]["functions_touched"].add(current_func)

        # Count changes
        if line.startswith("+") and not line.startswith("+++"):
            files[current_file]["lines_added"] += 1
            total_added += 1
        elif line.startswith("-") and not line.startswith("---"):
            files[current_file]["lines_removed"] += 1
            total_removed += 1

    # Convert sets to sorted lists
    for f in files.values():
        f["functions_touched"] = sorted(f["functions_touched"])
        f["classes_touched"] = sorted(f["classes_touched"])

    return {
        "files_changed": files_changed,
        "test_files_changed": test_files_changed,
        "total_lines_added": total_added,
        "total_lines_removed": total_removed,
        "files": files
    }

def use_unidiff(diff_text: str):
    patch = PatchSet(diff_text)
    facts = {
        "files_changed": len(patch),
        "test_files_changed": any("test" in file.path.lower() for file in patch),
        "total_lines_added": 0,
        "total_lines_removed": 0,
        "files": {}
    }

    for file in patch:
        file_info = {
            "lines_added": 0,
            "lines_removed": 0,
            "functions_touched": set(),
            "classes_touched": set()
        }

        for hunk in file:
            for line in hunk:
                if line.is_added:
                    file_info["lines_added"] += 1
                    facts["total_lines_added"] += 1
                elif line.is_removed:
                    file_info["lines_removed"] += 1
                    facts["total_lines_removed"] += 1

                # Check for function and class definitions

    return facts


if __name__ == "__main__":
    diff_dir = r"C:\Python\testing_data\sol2\rate_limiter_sol2\run_762eb055"
    diff_path = os.path.join(diff_dir, "git_diff.txt")
    with open(diff_path, "r", encoding="utf-8") as f:
        diff_text = f.read()

    facts = extract_diff_facts(diff_text)
    print("Custom Extraction:")    
    print(facts)
    facts_unidiff = use_unidiff(diff_text)
    print("Unidiff Extraction:")
    # Get keys in custom extraction not in unidiff extraction
    facts_unidiff["files"] = facts["files"]  # For easier comparison   

    save_path = os.path.join(diff_dir, "diff_facts.json")
    import json
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(facts, f, indent=2)