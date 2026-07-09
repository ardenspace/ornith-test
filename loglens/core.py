from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import ceil
from typing import Iterable, Mapping, Any


@dataclass(frozen=True)
class TopPath:
    path: str
    count: int


@dataclass(frozen=True)
class Summary:
    level_counts: dict[str, int]
    top_path: TopPath
    p95_duration: int | float


def aggregate_records(records: Iterable[Mapping[str, Any]]) -> Summary:
    materialized = list(records)
    level_counts = Counter(record["level"] for record in materialized)
    path_counts = Counter(record["path"] for record in materialized)
    top_path, top_count = min(
        path_counts.items(),
        key=lambda item: (-item[1], item[0]),
    )
    durations = sorted(record["duration"] for record in materialized)
    p95_index = ceil(0.95 * len(durations)) - 1
    return Summary(
        level_counts=dict(level_counts),
        top_path=TopPath(path=top_path, count=top_count),
        p95_duration=durations[p95_index],
    )
