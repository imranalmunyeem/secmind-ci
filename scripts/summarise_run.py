import json
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

def now_utc():
    return datetime.now(timezone.utc).isoformat()

def summarise(jsonl_path: Path, csv_path: Path, run_id: str):
    if not jsonl_path.exists():
        print(f"JSONL not found: {jsonl_path}")
        sys.exit(1)

    records = []
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    total_findings = len(records)
    unique_alerts = len(set(r["alert_name"] for r in records))

    row = {
        "run_id": run_id,
        "timestamp_utc": now_utc(),
        "total_findings": total_findings,
        "unique_alerts": unique_alerts
    }

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = csv_path.exists()

    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["run_id", "timestamp_utc", "total_findings", "unique_alerts"]
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    print("Run summary written:", row)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python summarise_run.py <jsonl> <csv> <run_id>")
        sys.exit(1)

    jsonl = Path(sys.argv[1])
    csv_file = Path(sys.argv[2])
    run_id = sys.argv[3]

    summarise(jsonl, csv_file, run_id)
