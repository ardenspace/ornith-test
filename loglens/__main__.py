from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import aggregate_records, is_valid_record


class InputError(Exception):
    pass


def load_records(path: Path):
    if not path.exists():
        raise InputError(f"input file not found: {path}")

    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            raise InputError(f"blank line at line {line_number}")
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise InputError(f"malformed JSON at line {line_number}") from exc
        if not is_valid_record(record):
            raise InputError(f"invalid record at line {line_number}")
        records.append(record)
    if not records:
        raise InputError("no records")
    return records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="loglens")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("file", type=Path)
    args = parser.parse_args(argv)

    try:
        records = load_records(args.file)
    except InputError as exc:
        print(str(exc), file=sys.stderr)
        return 1
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
