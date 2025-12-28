# Recursion Debugging Problem

This repository contains a small debugging exercise that tests knowledge of recursion in Python.

Task: find and fix the bug in the recursive function `factorial` located in `src/recursion.py` so that all tests pass.

What you'll find:
- [src/recursion.py](src/recursion.py) — a deliberately buggy recursive implementation of `factorial`.
- [tests/test_recursion.py](tests/test_recursion.py) — visible pytest tests that demonstrate the failing behavior.

Run the tests with:

```bash
python -m pip install -U pytest
pytest -q
```

Hint: consider the base case for `factorial(0)`.