import json
import hashlib
from pathlib import Path

def fingerprint(record: dict) -> str:
    """
    Stable fingerprint for a ZAP finding.
    We include additional fields to reduce collisions across findings.
    """
    alert = (record.get("alert_name") or "").strip()
    url = (record.get("url") or "").strip()
    param = (record.get("param") or "").strip()
    plugin_id = str(record.get("plugin_id") or "").strip()

    # Optional fields (may be empty depending on parser)
    method = (record.get("method") or "").strip()
    evidence = (record.get("evidence") or "").strip()

    key = f"{plugin_id}||{alert}||{method}||{url}||{param}||{evidence}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()

def load_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records

def load_seen(path: Path) -> set[str]:
    if not path.exists():
        return set()

    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return set()

    try:
        data = json.loads(raw)
        return set(data.get("seen", []))
    except json.JSONDecodeError:
        return set()

def save_seen(path: Path, seen: set[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"seen": sorted(seen)}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

def main():
    findings_path = Path("dataset/specs/zap_findings.jsonl")
    state_path = Path("dataset/state/seen_findings.json")
    out_new_path = Path("dataset/specs/new_findings.jsonl")

    if not findings_path.exists():
        raise FileNotFoundError(f"Missing {findings_path}")

    records = load_jsonl(findings_path)
    seen = load_seen(state_path)

    fps_all = [fingerprint(r) for r in records]
    print(f"Total findings: {len(records)}")
    print(f"Unique fingerprints (all findings): {len(set(fps_all))}")

    new_records = []
    new_fps = []

    for r in records:
        fp = fingerprint(r)
        if fp not in seen:
            new_records.append(r)
            new_fps.append(fp)

    print(f"New findings: {len(new_records)}")
    print(f"New fingerprints (this run): {len(set(new_fps))}")

    # Write new findings JSONL (may be empty)
    out_new_path.parent.mkdir(parents=True, exist_ok=True)
    with out_new_path.open("w", encoding="utf-8") as f:
        for r in new_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Update state
    updated_seen = set(seen)
    updated_seen.update(new_fps)
    save_seen(state_path, updated_seen)

    print(f"State size (seen): {len(updated_seen)}")
    print(f"Wrote: {out_new_path}")
    print(f"Updated: {state_path}")

if __name__ == "__main__":
    main()
