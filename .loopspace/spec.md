# Spec: LogLens
version: 1
status: approved

## Overview
LogLens is a small, same-day CLI experiment for summarizing a single sample NDJSON log file. It reads flat log records from one file and reports the minimum useful aggregate view: counts by `level`, the most frequent `path`, and p95 `duration`. The primary success path is running from the repository with no install step and immediately seeing a short, readable terminal summary.

## Goals
- Build a repo-local Python CLI that runs as `python -m loglens sample.ndjson` on macOS with Python 3.11.
- Read one NDJSON file containing sample log records with `level`, `path`, and `duration` fields.
- Produce concise text output that surfaces level counts, top path, and p95 duration without being verbose.
- Provide a JSON output mode for the same summary so the result can be reused programmatically.
- Include pytest coverage for the core sample-to-text-output flow.

## Non-Goals
- Realtime tailing.
- Multiple input files in one invocation.
- `.gz` or other compressed input.
- Time filtering.
- Custom group-by fields.
- UI or interactive display.
- Config files.
- Packaging, installation, plugin architecture, or service setup.
- Network or stdin input.
- Handling real production logs, secrets, credentials, PII, or redaction.

## Company Lens
This is a nice-to-have personal experiment intended to finish today. If it slips or fails, nobody else is blocked and the useful outcome can simply be learning whether this CLI shape is worth continuing. The MVP is intentionally narrow: a single sample NDJSON file, level count, top path, p95 duration, text/json CLI output, and passing pytest.

## User Lens
The only intended user for v1 is the project owner, who currently inspects similar logs with rough one-off scripts. The key effortless moment is typing `python -m loglens sample.ndjson` from inside the repository and immediately seeing a readable core summary. First-time zero-to-value should require no installation step. The main abandonment risk is output that is too long or fails to make the important summary obvious in the first minute.

## Engineer Lens
The v1 data set is sample-only, and the user confirmed it has no secrets, credentials, or PII. The only trust-boundary inputs are the CLI file path argument and the NDJSON file contents. Missing files, malformed JSON lines, blank lines, missing required fields, wrong field types, non-finite durations, and empty files must fail with specified stderr text and a non-zero exit code. v1 should avoid packaging, installation machinery, plugin systems, or other structural over-engineering; a simple Python module layout is sufficient. The core confidence test is a pytest case that runs the sample NDJSON through the text-output path and asserts exact expected summary content. Runtime target is macOS with Python 3.11.

## Designer Lens
Not applicable: no UI surface. CLI output still needs a simple information design: default text output is at most 5 non-empty lines and uses stable labels so the three core values are easy to find: `level_counts`, `top_path`, and `p95_duration`.

## Requirements
- R1: The repository provides a `loglens` Python module that can be executed from the repo root as `python -m loglens sample.ndjson` without an install step.
- R2: The CLI accepts exactly one NDJSON file path as its positional input for v1.
- R3: The repo root contains `sample.ndjson` with at least 3 valid NDJSON records; each record contains string `level`, string `path`, and finite numeric `duration` fields, where JSON booleans are not accepted as numeric durations.
- R4: For valid sample NDJSON records, the CLI computes counts grouped by each record's `level` value.
- R5: For valid sample NDJSON records, the CLI identifies the top path as the most frequent `path`; ties are resolved by choosing the lexicographically smallest path.
- R6: For valid sample NDJSON records, the CLI computes p95 over finite numeric `duration` values using the nearest-rank method: sort durations ascending and select index `ceil(0.95 * n) - 1`.
- R7: The default CLI output is text with at most 5 non-empty lines and contains the labels `level_counts`, `top_path`, and `p95_duration`.
- R8: The CLI provides JSON output via `python -m loglens --json sample.ndjson`.
- R9: JSON output is parseable JSON with exactly these top-level keys: `total_records` as an integer, `level_counts` as an object mapping level strings to integer counts, `top_path` as an object with `path` string and `count` integer, and `p95_duration` as a finite number.
- R10: When the input file path does not exist, the CLI writes stderr containing `input file not found` and the missing path, then exits with a non-zero status.
- R11: When any non-empty input line is malformed JSON, the CLI writes stderr containing `malformed JSON` and the 1-based line number, then exits with a non-zero status.
- R12: When any input line is blank or whitespace-only, the CLI writes stderr containing `blank line` and the 1-based line number, then exits with a non-zero status.
- R13: When an input record is missing `level`, `path`, or `duration`, or when `level`/`path` is not a string, or when `duration` is a JSON boolean or is not finite numeric, the CLI writes stderr containing `invalid record` and the 1-based line number, then exits with a non-zero status.
- R14: When the input file contains zero records, the CLI writes stderr containing `no records`, then exits with a non-zero status.
- R15: The project includes pytest coverage that runs `python -m loglens sample.ndjson` and asserts stdout contains `level_counts`, `top_path`, `p95_duration`, the exact expected level counts, the exact expected top path/count, and the exact expected p95 duration for the committed `sample.ndjson`.
- R16: The repository does not contain `pyproject.toml`, `setup.py`, `plugins/`, `ui/`, config files matching `config.*`, imports of `socket`, `urllib`, `requests`, or `httpx`, or reads from `sys.stdin`; `python -m loglens --help` does not contain `--tail`, `--follow`, `--gz`, `--since`, `--until`, `--time-filter`, or `--group-by`; and the CLI exits non-zero when invoked with more than one positional input file for v1.

## Approval
Approved by human on 2026-07-09. Open non-blocking issues at approval:
- Existing but unreadable input paths or directory paths are not separately specified beyond the general missing/invalid input behavior.
- No maximum file size, line length, or record count is specified for hostile oversized inputs; v1 is sample-only.
