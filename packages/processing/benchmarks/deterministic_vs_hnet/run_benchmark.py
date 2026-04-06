#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

DEFAULT_METRICS = [
    {"name": "retrieval_hit_rate_at_5", "direction": "higher_is_better"},
    {"name": "provenance_retention_rate", "direction": "higher_is_better"},
    {"name": "rerun_stability", "direction": "higher_is_better"},
    {"name": "mean_chunk_count", "direction": "lower_is_better"},
]


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Create a benchmark-run JSON skeleton from a corpus manifest and system declarations.")
    parser.add_argument("--corpus-manifest", required=True)
    parser.add_argument("--systems", required=True, help="JSON file containing a list of systems")
    parser.add_argument("--output", required=True)
    parser.add_argument("--benchmark-id", default="bench_det_vs_hnet_local")
    args = parser.parse_args()

    corpus_manifest = load_json(Path(args.corpus_manifest))
    systems = load_json(Path(args.systems))

    result = {
        "benchmark_id": args.benchmark_id,
        "benchmark_family": "chunking",
        "corpus_manifest_ref": args.corpus_manifest,
        "systems": systems,
        "metrics": DEFAULT_METRICS,
        "results": [
            {
                "system_id": system["system_id"],
                "metric_values": {},
                "notes": "Populate after executing retrieval and provenance checks"
            }
            for system in systems
        ]
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
