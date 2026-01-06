import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

def _now_iso():
    return datetime.now(timezone.utc).isoformat()

def parse_zap_report(report_path: Path, output_jsonl: Path, run_id: str = "local"):
    if not report_path.exists():
        raise FileNotFoundError(f"ZAP report not found: {report_path}")

    data = json.loads(report_path.read_text(encoding="utf-8", errors="ignore"))
    sites = data.get("site", [])
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with output_jsonl.open("w", encoding="utf-8") as f:
        for site in sites:
            alerts = site.get("alerts", [])
            for alert in alerts:
                instances = alert.get("instances", []) or [{}]
                for inst in instances:
                    record = {
                        "id": str(uuid.uuid4()),
                        "created_utc": _now_iso(),
                        "run_id": run_id,
                        "tool": "ZAP",
                        "alert_name": alert.get("alert"),
                        "risk": alert.get("riskdesc"),
                        "confidence": alert.get("confidence"),
                        "plugin_id": alert.get("pluginid"),
                        "cweid": alert.get("cweid"),
                        "url": inst.get("uri"),
                        "method": inst.get("method"),
                        "param": inst.get("param"),
                        "attack": inst.get("attack"),
                        "evidence": inst.get("evidence"),
                        "description": alert.get("desc"),
                        "solution": alert.get("solution"),
                        "reference": alert.get("reference"),
                        "test_intent": "Generate a deterministic security regression test for this finding",
                        "suggested_surface": "web",
                        "suggested_test_type": "dast-regression"
                    }
                    f.write(json.dumps(record) + "\n")
                    count += 1

    print(f"Wrote {count} records to {output_jsonl}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python parse_zap_json.py <report_json.json> <output.jsonl> <run_id>")
        sys.exit(1)

    report = Path(sys.argv[1])
    output = Path(sys.argv[2])
    run_id = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("GITHUB_RUN_ID", "local")

    parse_zap_report(report, output, run_id)
