import json
import math
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_loglens(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "loglens", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_json_cli_outputs_parseable_exact_sample_summary():
    result = run_loglens("--json", "sample.ndjson")

    assert result.returncode == 0, result.stderr
    parsed = json.loads(result.stdout)

    assert set(parsed) == {"total_records", "level_counts", "top_path", "p95_duration"}
    assert parsed == {
        "total_records": 4,
        "level_counts": {"info": 2, "error": 1, "warn": 1},
        "top_path": {"path": "/api/users", "count": 2},
        "p95_duration": 40,
    }

    assert isinstance(parsed["total_records"], int)
    assert not isinstance(parsed["total_records"], bool)
    assert isinstance(parsed["level_counts"], dict)
    assert all(isinstance(level, str) for level in parsed["level_counts"])
    assert all(
        isinstance(count, int) and not isinstance(count, bool)
        for count in parsed["level_counts"].values()
    )
    assert isinstance(parsed["top_path"], dict)
    assert isinstance(parsed["top_path"]["path"], str)
    assert isinstance(parsed["top_path"]["count"], int)
    assert not isinstance(parsed["top_path"]["count"], bool)
    assert isinstance(parsed["p95_duration"], (int, float))
    assert not isinstance(parsed["p95_duration"], bool)
    assert math.isfinite(parsed["p95_duration"])
