from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import aggregate_records


def load_records(path: Path):
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="loglens")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("file", type=Path)
    args = parser.parse_args(argv)

    records = load_records(args.file)
    summary = aggregate_records(records)
    if args.json_output:
        print(json.dumps({
            "total_records": len(records),
            "level_counts": summary.level_counts,
            "top_path": {
                "path": summary.top_path.path,
                "count": summary.top_path.count,
            },
            "p95_duration": summary.p95_duration,
        }))
        return 0

    print(f"level_counts: {summary.level_counts}")
    print(f"top_path: {summary.top_path.path} count={summary.top_path.count}")
    print(f"p95_duration: {summary.p95_duration}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
