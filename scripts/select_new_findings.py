import json
from pathlib import Path
from scripts.fingerprint_findings import fingerprint, load_jsonl

def load_seen(path: Path) -> set[str]:
    if not path.exists():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    return set(data.get("seen", []))

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

    new_records = []
    new_fps = []

    for r in records:
        fp = fingerprint(r)
        if fp not in seen:
            new_records.append(r)
            new_fps.append(fp)

    # write new_findings.jsonl (may be empty)
    out_new_path.parent.mkdir(parents=True, exist_ok=True)
    with out_new_path.open("w", encoding="utf-8") as f:
        for r in new_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # update state with new fingerprints
    updated_seen = set(seen)
    updated_seen.update(new_fps)
    save_seen(state_path, updated_seen)

    print(f"Total findings: {len(records)}")
    print(f"New findings: {len(new_records)}")
    print(f"State size (seen): {len(updated_seen)}")
    print(f"Wrote: {out_new_path}")
    print(f"Updated: {state_path}")

if __name__ == "__main__":
    main()
