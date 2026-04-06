#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def weighted_summary(metric_values):
    # Placeholder scoring model: retrieval and provenance dominate.
    retrieval = float(metric_values.get("retrieval_hit_rate_at_5", 0.0))
    provenance = float(metric_values.get("provenance_retention_rate", 0.0))
    stability = float(metric_values.get("rerun_stability", 0.0))
    chunk_penalty = float(metric_values.get("mean_chunk_count", 0.0))
    return round((0.4 * retrieval) + (0.35 * provenance) + (0.2 * stability) - (0.01 * chunk_penalty), 4)


def main():
    parser = argparse.ArgumentParser(description="Score a benchmark run JSON into a simple ranked summary.")
    parser.add_argument("--benchmark-run", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    benchmark_run = load_json(Path(args.benchmark_run))
    rankings = []
    for result in benchmark_run.get("results", []):
        score = weighted_summary(result.get("metric_values", {}))
        rankings.append({
            "system_id": result["system_id"],
            "score": score,
            "metric_values": result.get("metric_values", {})
        })

    rankings.sort(key=lambda item: item["score"], reverse=True)
    payload = {
        "benchmark_id": benchmark_run.get("benchmark_id"),
        "rankings": rankings
    }
    with Path(args.output).open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
