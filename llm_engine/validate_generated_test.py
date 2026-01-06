from pathlib import Path
import ast
import sys

ALLOWED_IMPORTS = {"requests", "pytest", "re", "json"}

def validate_python_test(path: Path):
    code = path.read_text(encoding="utf-8", errors="ignore")
    tree = ast.parse(code)

    has_assert = any(isinstance(n, ast.Assert) for n in ast.walk(tree))
    if not has_assert:
        raise ValueError(f"{path.name}: missing assert statement")

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] not in ALLOWED_IMPORTS:
                    raise ValueError(f"{path.name}: disallowed import: {alias.name}")
        if isinstance(node, ast.ImportFrom):
            mod = (node.module or "").split(".")[0]
            if mod and mod not in ALLOWED_IMPORTS:
                raise ValueError(f"{path.name}: disallowed import-from: {node.module}")

def main(target: str):
    p = Path(target)

    if p.is_dir():
        files = sorted(p.glob("*.py"))
        if not files:
            print(f"No .py tests found in directory: {p}")
            sys.exit(1)
        for f in files:
            validate_python_test(f)
            print("Validation OK:", f)
        return

    if p.is_file():
        validate_python_test(p)
        print("Validation OK:", p)
        return

    print(f"Path not found: {p}")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_generated_test.py <file_or_directory>")
        sys.exit(1)

    main(sys.argv[1])
