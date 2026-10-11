#!/usr/bin/env python3
"""Build charts + DATASET_CARD.md from the annotations of one annotator.

Usage:  python scripts/stats.py --annotator main
Outputs: reports/event_counts.png, reports/shot_types.png, reports/clip_durations.png, DATASET_CARD.md
"""
import argparse
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import REPORTS_DIR, ROOT, load_annotations, load_provenance

COLOR = "#2f6f4e"


def bar(counter: Counter, title: str, path: Path, horizontal=False):
    if not counter:
        return False
    items = counter.most_common()
    labels, vals = [k for k, _ in items], [v for _, v in items]
    fig, ax = plt.subplots(figsize=(7, 3.8))
    (ax.barh if horizontal else ax.bar)(labels, vals, color=COLOR)
    if horizontal:
        ax.invert_yaxis()
    ax.set_title(title, loc="left", fontsize=12)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for i, v in enumerate(vals):
        (ax.text(v, i, f" {v}", va="center") if horizontal else ax.text(i, v, str(v), ha="center", va="bottom"))
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--annotator", default="main")
    a = ap.parse_args()

    prov = load_provenance()
    ann = [d for _, _, d, e in load_annotations(a.annotator) if d]
    events = [e for d in ann for e in d["events"]]
    REPORTS_DIR.mkdir(exist_ok=True)

    type_counts = Counter(e["type"] for e in events)
    shots = Counter(e["shot_type"] for e in events if e["type"] == "shot")
    dismissals = Counter(e["dismissal"] for e in events if e["type"] == "wicket")
    outcomes = Counter(e["outcome"] for e in events if e["type"] == "delivery")
    conf = Counter(e["confidence"] for e in events)
    bar(type_counts, "Events per type", REPORTS_DIR / "event_counts.png")
    bar(shots, "Shot types", REPORTS_DIR / "shot_types.png", horizontal=True)

    durs = [float(r["duration_s"]) for r in prov.values() if r.get("duration_s")]
    if durs:
        fig, ax = plt.subplots(figsize=(7, 3.2))
        ax.hist(durs, bins=min(10, max(3, len(durs))), color=COLOR)
        ax.set_title("Clip durations (s)", loc="left", fontsize=12)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        fig.tight_layout()
        fig.savefig(REPORTS_DIR / "clip_durations.png", dpi=160)
        plt.close(fig)

    licences = Counter(r["licence"] for r in prov.values())
    platforms = Counter(r["source_platform"] for r in prov.values())

    def table(c: Counter) -> str:
        return "\n".join(f"| {k} | {v} |" for k, v in c.most_common()) or "| - | 0 |"

    card = f"""# Dataset card: Cricket event annotation set

**Schema version:** 1.0.0  **Annotator:** `{a.annotator}`

## Size
- Clips: **{len(prov)}** ({sum(durs):.0f} s total, mean {sum(durs)/len(durs) if durs else 0:.0f} s)
- Annotated clips: **{len(ann)}**
- Events: **{len(events)}**

## Event type distribution
| type | count |
|---|---|
{table(type_counts)}

## Shot types
| shot_type | count |
|---|---|
{table(shots)}

## Delivery outcomes
| outcome | count |
|---|---|
{table(outcomes)}

## Dismissals
| dismissal | count |
|---|---|
{table(dismissals)}

## Label confidence
| confidence | count |
|---|---|
{table(conf)}

## Provenance
| source platform | clips |
|---|---|
{table(platforms)}

| licence | clips |
|---|---|
{table(licences)}

Every clip has a source URL (or is self-recorded), licence, collection date and SHA-256 in `data/provenance.csv`.
Raw video is not redistributed in this repository.

## Known limitations
_Fill these in honestly. Examples: small sample; mostly one camera angle; class imbalance (few wickets);
single primary annotator, agreement measured on N clips only; no ball-tracking labels._

## Intended use
Prototype event-segmentation and shot-classification experiments; not a benchmark.
"""
    (ROOT / "DATASET_CARD.md").write_text(card, encoding="utf-8")
    print(card)


if __name__ == "__main__":
    main()
