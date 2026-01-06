from pathlib import Path

def count_py(path: Path) -> int:
    if not path.exists():
        return 0
    return len(list(path.glob("*.py")))

if __name__ == "__main__":
    print(count_py(Path("tests_generated/api")))
