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


def test_text_cli_summarizes_sample_ndjson_from_repo_root():
    result = run_loglens("sample.ndjson")

    assert result.returncode == 0, result.stderr
    non_empty_lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert len(non_empty_lines) <= 5
    assert "level_counts" in result.stdout
    assert "{'info': 2, 'error': 1, 'warn': 1}" in result.stdout
    assert "top_path: /api/users count=2" in non_empty_lines
    assert "p95_duration" in result.stdout
    assert "p95_duration: 40" in non_empty_lines


def test_text_cli_requires_one_file_argument():
    result = run_loglens()

    assert result.returncode != 0
