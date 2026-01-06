from pathlib import Path

if __name__ == "__main__":
    p = Path("tests_generated/api")
    if not p.exists():
        print(0)
    else:
        print(len(list(p.glob("*.py"))))
