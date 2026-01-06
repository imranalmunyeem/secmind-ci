import json
import hashlib
import re
from pathlib import Path

def fingerprint(record: dict) -> str:
    alert = (record.get("alert_name") or "").strip()
    url = (record.get("url") or "").strip()
    param = (record.get("param") or "").strip()
    plugin_id = str(record.get("plugin_id") or "").strip()
    key = f"{plugin_id}||{alert}||{url}||{param}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]

def slugify(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")[:50] or "alert"

def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                out.append(json.loads(line))
    return out

def write_test(record: dict, out_dir: Path) -> Path:
    alert = record.get("alert_name") or "Unknown Alert"
    url = record.get("url") or "http://localhost:3000"
    fp = fingerprint(record)
    name = slugify(alert)

    out_file = out_dir / f"test_{name}_{fp}.py"

    code = f'''"""
AUTO-GENERATED SECURITY REGRESSION TEST (CONTINUOUS MODE)
alert_name: {alert}
url: {url}
fingerprint: {fp}
"""

import requests

def test_{name}_{fp}():
    r = requests.get("{url}", timeout=10)
    print("status:", r.status_code)
    print("headers:", dict(r.headers))

    # Deterministic baseline assertion: service must not error 5xx
    assert r.status_code < 500, f"Server error: {{r.status_code}}"
'''
    out_file.write_text(code, encoding="utf-8")
    return out_file

def main():
    in_path = Path("dataset/specs/new_findings.jsonl")
    out_dir = Path("tests_generated/api")
    out_dir.mkdir(parents=True, exist_ok=True)

    records = read_jsonl(in_path)

    if not records:
        print("No NEW findings. No tests generated.")
        return

    created = 0
    for r in records:
        out_file = write_test(r, out_dir)
        created += 1
        print("Generated:", out_file)

    print(f"Generated {created} test(s) from NEW findings.")

if __name__ == "__main__":
    main()
