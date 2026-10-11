"""Shared helpers: paths, provenance + annotation loading."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schema" / "event_schema.json"
PROVENANCE_PATH = ROOT / "data" / "provenance.csv"
ANNOTATIONS_DIR = ROOT / "data" / "annotations"
CLIPS_DIR = ROOT / "data" / "clips"
REPORTS_DIR = ROOT / "reports"

PROVENANCE_FIELDS = [
    "clip_id", "filename", "source_platform", "source_url", "author", "licence",
    "licence_url", "collected_on", "sha256", "duration_s", "fps", "width", "height", "notes",
]
REQUIRED_PROVENANCE = ["clip_id", "source_platform", "licence", "collected_on", "sha256", "duration_s"]


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while block := f.read(chunk):
            h.update(block)
    return h.hexdigest()


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_provenance(path: Path = PROVENANCE_PATH) -> dict[str, dict]:
    if not path.exists():
        return {}
    with open(path, newline="", encoding="utf-8") as f:
        return {row["clip_id"]: row for row in csv.DictReader(f)}


def load_annotations(annotator: str | None = None, root: Path = ANNOTATIONS_DIR):
    """Yield (annotator, path, data_or_None, error_or_None) for every annotation JSON."""
    for adir in sorted(p for p in root.iterdir() if p.is_dir()):
        if annotator and adir.name != annotator:
            continue
        for p in sorted(adir.glob("*.json")):
            try:
                yield adir.name, p, json.loads(p.read_text(encoding="utf-8")), None
            except json.JSONDecodeError as e:
                yield adir.name, p, None, str(e)
