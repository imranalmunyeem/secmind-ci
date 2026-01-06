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

def summarise(all_findings_jsonl: Path,
             new_findings_jsonl: Path,
             csv_path: Path,
             run_id: str,
             tests_generated_total: int,
             zap_seconds: float,
             pipeline_seconds: float):
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
        "new_tests_generated": tests_generated_total,
        "zap_duration_seconds": round(zap_seconds, 3),
        "pipeline_duration_seconds": round(pipeline_seconds, 3),
    }

    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(row.keys())
        )
        writer.writeheader()
        writer.writerow(row)

    print("Run summary written:", row)

if __name__ == "__main__":
    if len(sys.argv) < 8:
        print("Usage: python summarise_run.py <all_findings_jsonl> <new_findings_jsonl> <csv> <run_id> <tests_generated_total_int> <zap_seconds_float> <pipeline_seconds_float>")
        sys.exit(1)

    summarise(
        Path(sys.argv[1]),
        Path(sys.argv[2]),
        Path(sys.argv[3]),
        sys.argv[4],
        int(sys.argv[5]),
        float(sys.argv[6]),
        float(sys.argv[7]),
    )
