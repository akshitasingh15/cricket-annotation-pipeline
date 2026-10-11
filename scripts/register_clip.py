#!/usr/bin/env python3
"""Register a clip: hash it, probe it, and append a provenance row.

Example:
  python scripts/register_clip.py data/clips/nets_cover_drive_01.mp4 \
      --platform "Pexels" --url "https://www.pexels.com/video/..." \
      --licence "Pexels License" --licence-url "https://www.pexels.com/license/" \
      --author "Jane Doe"

For clips you filmed yourself use: --platform self_recorded --licence "Own work" --author "<you>"
"""
import argparse
import csv
import datetime as dt
import re
import sys
from pathlib import Path

import cv2

from common import PROVENANCE_FIELDS, PROVENANCE_PATH, load_provenance, sha256_file


def probe(path: Path) -> dict:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        sys.exit(f"Cannot open video: {path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 0
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
    out = {
        "fps": round(fps, 3),
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "duration_s": round(frames / fps, 3) if fps else 0,
    }
    cap.release()
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", type=Path)
    ap.add_argument("--platform", required=True, help="e.g. Pexels, Wikimedia Commons, YouTube (CC BY), self_recorded")
    ap.add_argument("--url", default="", help="source page URL (leave blank for self-recorded)")
    ap.add_argument("--licence", required=True, help='e.g. "CC BY 3.0", "Pexels License", "Own work"')
    ap.add_argument("--licence-url", default="")
    ap.add_argument("--author", default="")
    ap.add_argument("--notes", default="")
    a = ap.parse_args()

    if not a.video.exists():
        sys.exit(f"File not found: {a.video}")
    clip_id = re.sub(r"[^a-z0-9_]+", "_", a.video.stem.lower()).strip("_")
    if clip_id != a.video.stem:
        print(f"Note: clip_id normalised to '{clip_id}'. Rename the file to '{clip_id}{a.video.suffix}' "
              "so the annotator and QA scripts can match it.")

    digest = sha256_file(a.video)
    existing = load_provenance()
    if clip_id in existing:
        sys.exit(f"clip_id '{clip_id}' already registered.")
    for row in existing.values():
        if row["sha256"] == digest:
            sys.exit(f"Duplicate content: identical to already-registered clip '{row['clip_id']}'.")

    meta = probe(a.video)
    row = {
        "clip_id": clip_id, "filename": a.video.name, "source_platform": a.platform,
        "source_url": a.url, "author": a.author, "licence": a.licence, "licence_url": a.licence_url,
        "collected_on": dt.date.today().isoformat(), "sha256": digest, "notes": a.notes, **meta,
    }
    new_file = not PROVENANCE_PATH.exists()
    with open(PROVENANCE_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=PROVENANCE_FIELDS)
        if new_file:
            w.writeheader()
        w.writerow(row)
    print(f"Registered {clip_id}: {meta['duration_s']}s, {meta['width']}x{meta['height']} @ {meta['fps']} fps, sha256={digest[:12]}...")


if __name__ == "__main__":
    main()
