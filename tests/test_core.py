import json
import math
from pathlib import Path

from loglens.core import aggregate_records


ROOT = Path(__file__).resolve().parents[1]


def load_sample_records():
    records = []
    for line in (ROOT / "sample.ndjson").read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def test_sample_ndjson_records_are_valid():
    records = load_sample_records()
    assert len(records) >= 3
    for record in records:
        assert isinstance(record["level"], str)
        assert isinstance(record["path"], str)
        assert isinstance(record["duration"], (int, float))
        assert not isinstance(record["duration"], bool)
        assert math.isfinite(record["duration"])


def test_sample_level_counts_are_exact():
    summary = aggregate_records(load_sample_records())
    assert summary.level_counts == {"info": 2, "error": 1, "warn": 1}


def test_sample_top_path_and_lexicographic_tie_behavior():
    summary = aggregate_records(load_sample_records())
    assert summary.top_path.path == "/api/users"
    assert summary.top_path.count == 2

    tied = aggregate_records([
        {"level": "info", "path": "/b", "duration": 1},
        {"level": "info", "path": "/a", "duration": 2},
        {"level": "info", "path": "/b", "duration": 3},
        {"level": "info", "path": "/a", "duration": 4},
    ])
    assert tied.top_path.path == "/a"
    assert tied.top_path.count == 2


def test_nearest_rank_p95_duration_for_sample_and_non_final_index_case():
    summary = aggregate_records(load_sample_records())
    assert summary.p95_duration == 40

    records = [
        {"level": "info", "path": "/p", "duration": duration}
        for duration in range(1, 22)
    ]
    # ceil(0.95 * 21) - 1 == 19, selecting 20 rather than final value 21.
    assert aggregate_records(records).p95_duration == 20
