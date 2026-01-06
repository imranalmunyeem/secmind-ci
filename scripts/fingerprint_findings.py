import json
import hashlib
from pathlib import Path

def fingerprint(record: dict) -> str:
    """
    Stable fingerprint for a ZAP finding instance.
    We use fields that define a "unique issue surface".
    """
    alert = (record.get("alert_name") or "").strip()
    url = (record.get("url") or "").strip()
    param = (record.get("param") or "").strip()
    plugin_id = str(record.get("plugin_id") or "").strip()

    key = f"{plugin_id}||{alert}||{url}||{param}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()

def load_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records

if __name__ == "__main__":
    # quick local check (optional)
    p = Path("dataset/specs/zap_findings.jsonl")
    if p.exists():
        recs = load_jsonl(p)
        print("records:", len(recs))
        if recs:
            print("example fingerprint:", fingerprint(recs[0]))
