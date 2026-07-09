import json
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


def write_ndjson(path: Path, records: list[object]) -> None:
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")


def assert_cli_error(result: subprocess.CompletedProcess[str], *expected: str) -> None:
    assert result.returncode != 0
    for text in expected:
        assert text in result.stderr


def test_missing_input_file_reports_path():
    result = run_loglens("does-not-exist.ndjson")

    assert_cli_error(result, "input file not found", "does-not-exist.ndjson")


def test_malformed_json_reports_one_based_line_number(tmp_path):
    path = tmp_path / "bad.ndjson"
    path.write_text(
        json.dumps({"level": "info", "path": "/ok", "duration": 1}) + "\n{not json}\n",
        encoding="utf-8",
    )

    result = run_loglens(str(path))

    assert_cli_error(result, "malformed JSON", "2")


def test_blank_line_reports_one_based_line_number(tmp_path):
    path = tmp_path / "blank.ndjson"
    path.write_text(
        json.dumps({"level": "info", "path": "/ok", "duration": 1}) + "\n   \n",
        encoding="utf-8",
    )

    result = run_loglens(str(path))

    assert_cli_error(result, "blank line", "2")


def test_invalid_records_report_one_based_line_number(tmp_path):
    valid = {"level": "info", "path": "/ok", "duration": 1}
    invalid_cases = [
        {"path": "/bad", "duration": 1},
        {"level": "info", "duration": 1},
        {"level": "info", "path": "/bad"},
        {"level": 1, "path": "/bad", "duration": 1},
        {"level": "info", "path": 1, "duration": 1},
        {"level": "info", "path": "/bad", "duration": True},
        {"level": "info", "path": "/bad", "duration": "1"},
        {"level": "info", "path": "/bad", "duration": float("inf")},
    ]

    for index, invalid in enumerate(invalid_cases):
        path = tmp_path / f"invalid-{index}.ndjson"
        write_ndjson(path, [valid, invalid])

        result = run_loglens(str(path))

        assert_cli_error(result, "invalid record", "2")


def test_empty_file_reports_no_records(tmp_path):
    path = tmp_path / "empty.ndjson"
    path.write_text("", encoding="utf-8")

    result = run_loglens(str(path))

    assert_cli_error(result, "no records")
