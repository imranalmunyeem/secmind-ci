from pathlib import Path
import ast

ALLOWED_IMPORTS = {"requests", "pytest", "re", "json"}

def validate_python_test(path: Path):
    code = path.read_text(encoding="utf-8", errors="ignore")
    tree = ast.parse(code)

    has_assert = any(isinstance(n, ast.Assert) for n in ast.walk(tree))
    if not has_assert:
        raise ValueError("Generated test has no assert statement.")

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] not in ALLOWED_IMPORTS:
                    raise ValueError(f"Disallowed import: {alias.name}")
        if isinstance(node, ast.ImportFrom):
            mod = (node.module or "").split(".")[0]
            if mod and mod not in ALLOWED_IMPORTS:
                raise ValueError(f"Disallowed import-from: {node.module}")

    return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python validate_generated_test.py <path_to_test.py>")
        raise SystemExit(1)

    # allow wildcard expansion by the shell in CI; Python receives actual filename(s)
    for arg in sys.argv[1:]:
        p = Path(arg)
        validate_python_test(p)
        print("Validation OK:", p)
