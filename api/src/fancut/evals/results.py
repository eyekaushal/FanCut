"""Recorded results: the JSON files the evaluation commands write, which the API serves
and the Studio shows. Missing files are simply absent, never an error."""

import json
from pathlib import Path
from typing import Any

RESULTS_DIR = Path(__file__).parent / "results"
FILES = ("director", "redteam", "foundry")


def load_results(directory: Path = RESULTS_DIR) -> dict[str, dict[str, Any] | None]:
    found: dict[str, dict[str, Any] | None] = {}
    for name in FILES:
        path = directory / f"{name}.json"
        try:
            data = json.loads(path.read_text()) if path.exists() else None
        except (OSError, ValueError):
            data = None
        found[name] = data if isinstance(data, dict) else None
    return found


def save_result(name: str, data: Any, directory: Path = RESULTS_DIR) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return path
