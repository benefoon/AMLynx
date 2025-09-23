from __future__ import annotations

from typing import Callable, Iterable, Iterator, List, Dict, Any
import csv
from pathlib import Path


def read_csv_stream(path: Path, chunk_size: int = 10_000) -> Iterator[List[Dict[str, Any]]]:
    with path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        chunk: List[Dict[str, Any]] = []
        for row in reader:
            chunk.append(row)
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk


def transform_chunk(chunk: List[Dict[str, Any]], *transforms: Callable[[Dict[str, Any]], Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for row in chunk:
        for t in transforms:
            row = t(row)
        out.append(row)
    return out
