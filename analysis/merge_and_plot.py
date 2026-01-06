from __future__ import annotations

import glob
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def find_all_runs_csv(root: Path) -> list[Path]:
    # We downloaded artifacts to analysis/raw/<run_id>/...
    pattern = str(root / "raw" / "**" / "dataset" / "results" / "runs.csv")
    return [Path(p) for p in glob.glob(pattern, recursive=True)]


def load_and_merge(csv_files: list[Path]) -> pd.DataFrame:
    frames = []
    for f in csv_files:
        try:
            df = pd.read_csv(f)
            df["source_file"] = str(f)
            frames.append(df)
        except Exception as e:
            print(f"Skipping {f} due to error: {e}")

    if not frames:
        raise RuntimeError("No runs.csv files found to merge.")

    merged = pd.concat(frames, ignore_index=True)

    # Ensure consistent dtypes
    for col in [
        "total_findings",
        "unique_alerts",
        "new_findings",
        "new_tests_generated",
        "zap_duration_seconds",
        "pipeline_duration_seconds",
    ]:
        if col in merged.columns:
            merged[col] = pd.to_numeric(merged[col], errors="coerce")

    # Parse timestamp if present
    if "timestamp_utc" in merged.columns:
        merged["timestamp_utc"] = pd.to_datetime(merged["timestamp_utc"], errors="coerce", utc=True)

    # Sort by time if possible
    if "timestamp_utc" in merged.columns and merged["timestamp_utc"].notna().any():
        merged = merged.sort_values("timestamp_utc").reset_index(drop=True)

    # Derived metrics
    if "pipeline_duration_seconds" in merged.columns and "zap_duration_seconds" in merged.columns:
        merged["overhead_seconds"] = merged["pipeline_duration_seconds"] - merged["zap_duration_seconds"]

    return merged


def save_summary(merged: pd.DataFrame, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = out_dir / "summary.txt"

    lines = []
    lines.append(f"total_runs: {len(merged)}")
    for col in ["total_findings", "unique_alerts", "new_findings", "new_tests_generated", "zap_duration_seconds", "pipeline_duration_seconds", "overhead_seconds"]:
        if col in merged.columns:
            lines.append(f"\n[{col}]")
            lines.append(str(merged[col].describe()))

    summary_path.write_text("\n".join(lines), encoding="utf-8")
    print("Wrote summary:", summary_path)


def plot_series(merged: pd.DataFrame, x_col: str, y_col: str, out_path: Path, title: str, xlabel: str, ylabel: str):
    plt.figure()
    plt.plot(merged[x_col], merged[y_col])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()
    print("Saved plot:", out_path)


def main():
    root = Path("analysis")
    out_dir = root / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_files = find_all_runs_csv(root)
    print(f"Found {len(csv_files)} runs.csv files")
    if len(csv_files) == 0:
        raise RuntimeError("No runs.csv files found. Ensure artifacts downloaded to analysis/raw/<run_id>/...")

    merged = load_and_merge(csv_files)

    # Save merged csv
    merged_csv_path = out_dir / "merged_runs.csv"
    merged.to_csv(merged_csv_path, index=False)
    print("Wrote merged CSV:", merged_csv_path)

    # Save summary stats
    save_summary(merged, out_dir)

    # Choose x-axis
    if "timestamp_utc" in merged.columns and merged["timestamp_utc"].notna().any():
        x_col = "timestamp_utc"
        xlabel = "Time (UTC)"
    else:
        x_col = "run_id"
        xlabel = "Run ID"

    # Make plots (paper-friendly)
    if "total_findings" in merged.columns:
        plot_series(merged, x_col, "total_findings", out_dir / "plot_total_findings.png",
                    "Total Findings Over Runs", xlabel, "Total Findings")

    if "new_findings" in merged.columns:
        plot_series(merged, x_col, "new_findings", out_dir / "plot_new_findings.png",
                    "New Findings Over Runs", xlabel, "New Findings")

    if "new_tests_generated" in merged.columns:
        plot_series(merged, x_col, "new_tests_generated", out_dir / "plot_new_tests_generated.png",
                    "New Tests Generated Over Runs", xlabel, "New Tests Generated")

    if "zap_duration_seconds" in merged.columns:
        plot_series(merged, x_col, "zap_duration_seconds", out_dir / "plot_zap_duration.png",
                    "ZAP Scan Duration Over Runs", xlabel, "Seconds")

    if "pipeline_duration_seconds" in merged.columns:
        plot_series(merged, x_col, "pipeline_duration_seconds", out_dir / "plot_pipeline_duration.png",
                    "Pipeline Duration Over Runs", xlabel, "Seconds")

    if "overhead_seconds" in merged.columns:
        plot_series(merged, x_col, "overhead_seconds", out_dir / "plot_overhead_seconds.png",
                    "Framework Overhead (Pipeline - ZAP) Over Runs", xlabel, "Seconds")


if __name__ == "__main__":
    main()
