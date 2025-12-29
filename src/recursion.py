def factorial(n: int) -> int:
    """Return n! using recursion.

    Deliberately contains a bug for the exercise: the base case for 0 is wrong.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    # BUG: this returns 0 for n == 0, but should return 1
    if n == 0:
        return 1        
    return n * factorial(n - 1)


if __name__ == "__main__":
    # Quick demonstration (will show the bug for 0)
    print("5! =", factorial(5))
    print("0! =", factorial(0))
