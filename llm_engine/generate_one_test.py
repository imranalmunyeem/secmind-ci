import json
import re
from pathlib import Path

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")[:60] or "alert"

def main():
    specs_path = Path("dataset/specs/zap_findings.jsonl")
    out_dir = Path("tests_generated/api")
    out_dir.mkdir(parents=True, exist_ok=True)

    if not specs_path.exists():
        raise FileNotFoundError(f"Missing {specs_path}. Run CI parse step first.")

    # take first record only (newbie-friendly)
    first = None
    with specs_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                first = json.loads(line)
                break

    if not first:
        raise RuntimeError("No findings found in JSONL.")

    url = first.get("url") or "http://localhost:3000"
    alert = first.get("alert_name") or "Unknown Alert"
    fname = f"test_{slugify(alert)}.py"
    out_file = out_dir / fname

    # A very simple deterministic regression check:
    # Fetch URL and assert response is not a server error.
    # Later we will generate vulnerability-specific assertions with an LLM.
    test_code = f'''"""
AUTO-GENERATED SECURITY REGRESSION TEST
Source: ZAP finding
Alert: {alert}
URL: {url}
"""

import requests

def test_generated_{slugify(alert)}():
    r = requests.get("{url}", timeout=15)
    assert r.status_code < 500, f"Server error status: {{r.status_code}}"
'''
    out_file.write_text(test_code, encoding="utf-8")
    print(f"Generated: {out_file}")

if __name__ == "__main__":
    main()
