import json
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

def now_utc():
    return datetime.now(timezone.utc).isoformat()

def count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    n = 0
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                n += 1
    return n

def load_records(jsonl_path: Path) -> list[dict]:
    records = []
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records

def summarise(all_findings_jsonl: Path, new_findings_jsonl: Path, csv_path: Path, run_id: str, tests_generated: int):
    if not all_findings_jsonl.exists():
        print(f"JSONL not found: {all_findings_jsonl}")
        sys.exit(1)

    records = load_records(all_findings_jsonl)

    total_findings = len(records)
    unique_alerts = len(set(r.get("alert_name") for r in records if r.get("alert_name")))
    new_findings = count_jsonl(new_findings_jsonl)

    row = {
        "run_id": run_id,
        "timestamp_utc": now_utc(),
        "total_findings": total_findings,
        "unique_alerts": unique_alerts,
        "new_findings": new_findings,
        "new_tests_generated": tests_generated
    }

    csv_path.parent.mkdir(parents=True, exist_ok=True)

    # IMPORTANT (Option B):
    # This CSV is per-run and will be uploaded as artifact (not appended across runs).
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["run_id", "timestamp_utc", "total_findings", "unique_alerts", "new_findings", "new_tests_generated"]
        )
        writer.writeheader()
        writer.writerow(row)

    print("Run summary written:", row)

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: python summarise_run.py <all_findings_jsonl> <new_findings_jsonl> <csv> <run_id> <tests_generated_int>")
        sys.exit(1)

    summarise(
        Path(sys.argv[1]),
        Path(sys.argv[2]),
        Path(sys.argv[3]),
        sys.argv[4],
        int(sys.argv[5])
    )
