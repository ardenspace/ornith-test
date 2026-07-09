# Plan: LogLens
version: 1
status: approved

## Phase 1: Text summary MVP
Goal: A valid committed sample NDJSON file can be summarized from the repo root with `python -m loglens sample.ndjson` and verified by pytest.
Phase acceptance: From the repo root, `python -m pytest` passes and `python -m loglens sample.ndjson` exits 0 with at most 5 non-empty stdout lines containing `level_counts`, `top_path`, and `p95_duration` plus exact expected values for the committed sample file.

### Task 1.1: Sample data and aggregation core
risk: light
covers: R3, R4, R5, R6
files: sample.ndjson, loglens/core.py, tests/test_core.py
acceptance:
- `sample.ndjson` exists at the repo root and contains at least 3 non-empty NDJSON records, each with string `level`, string `path`, and finite numeric non-boolean `duration`.
- A pytest test imports the aggregation function and asserts exact `level_counts` for the committed `sample.ndjson`.
- A pytest test imports the aggregation function and asserts exact `top_path.path` and `top_path.count` for the committed `sample.ndjson`, including lexicographic tie behavior in a dedicated in-memory case.
- A pytest test imports the aggregation function and asserts exact nearest-rank p95 duration for the committed `sample.ndjson` and for an in-memory list where `ceil(0.95 * n) - 1` selects a non-final sorted index.

### Task 1.2: Repo-local text CLI path
risk: heavy
covers: R1, R2, R7, R15
files: loglens/__main__.py, loglens/core.py, tests/test_cli_text.py
acceptance:
- From the repo root, `python -m loglens sample.ndjson` exits 0 without running an install command.
- The default stdout from `python -m loglens sample.ndjson` has at most 5 non-empty lines.
- The default stdout contains `level_counts`, `top_path`, and `p95_duration`.
- A pytest test runs `python -m loglens sample.ndjson` as a subprocess and asserts stdout contains the exact expected level counts, exact expected top path/count, and exact expected p95 duration for the committed `sample.ndjson`.
- Invoking the CLI with zero positional file arguments exits non-zero.

## Phase 2: JSON mode, validation, and scope guard
Goal: The CLI exposes the specified JSON output, fails predictably for invalid inputs, and stays inside the v1 non-goal boundaries.
Phase acceptance: From the repo root, `python -m pytest` passes; valid text and JSON invocations exit 0; specified invalid inputs exit non-zero with required stderr substrings; and scope-guard tests prove no forbidden files, imports, help flags, stdin reads, or multi-file behavior were introduced.

### Task 2.1: JSON output mode
risk: light
covers: R8, R9
files: loglens/__main__.py, tests/test_cli_json.py
acceptance:
- `python -m loglens --json sample.ndjson` exits 0.
- A pytest test parses stdout from `python -m loglens --json sample.ndjson` with `json.loads`.
- Parsed JSON has exactly the top-level keys `total_records`, `level_counts`, `top_path`, and `p95_duration`.
- Parsed JSON has `total_records` as an integer, `level_counts` as an object mapping strings to integers, `top_path.path` as a string, `top_path.count` as an integer, and `p95_duration` as a finite non-boolean number.
- Parsed JSON values match the exact expected summary for the committed `sample.ndjson`.

### Task 2.2: Input failure handling
risk: heavy
covers: R10, R11, R12, R13, R14
files: loglens/__main__.py, loglens/core.py, tests/test_cli_errors.py
acceptance:
- A pytest test invokes `python -m loglens does-not-exist.ndjson` and asserts non-zero exit plus stderr containing `input file not found` and `does-not-exist.ndjson`.
- A pytest test invokes the CLI on a file with malformed JSON on line 2 and asserts non-zero exit plus stderr containing `malformed JSON` and `2`.
- A pytest test invokes the CLI on a file with a blank or whitespace-only line at line 2 and asserts non-zero exit plus stderr containing `blank line` and `2`.
- A pytest test invokes the CLI on files with missing `level`, missing `path`, missing `duration`, non-string `level`, non-string `path`, boolean `duration`, non-numeric `duration`, and non-finite `duration`, and each case exits non-zero with stderr containing `invalid record` and the relevant 1-based line number.
- A pytest test invokes the CLI on an empty file and asserts non-zero exit plus stderr containing `no records`.

### Task 2.3: V1 scope guard
risk: light
covers: R16
files: tests/test_scope_guard.py
acceptance:
- A pytest test asserts the repo root does not contain `pyproject.toml`, `setup.py`, `plugins/`, or `ui/`.
- A pytest test asserts no repo file outside `.git`, `.opencode`, `.loopspace`, and test cache directories matches `config.*`.
- A pytest test scans project Python files outside tests and asserts they do not import `socket`, `urllib`, `requests`, or `httpx`.
- A pytest test scans project Python files outside tests and asserts they do not read from `sys.stdin`.
- A pytest test runs `python -m loglens --help` and asserts stdout does not contain `--tail`, `--follow`, `--gz`, `--since`, `--until`, `--time-filter`, or `--group-by`.
- A pytest test invokes `python -m loglens sample.ndjson sample.ndjson` and asserts a non-zero exit.

## Re-plans
