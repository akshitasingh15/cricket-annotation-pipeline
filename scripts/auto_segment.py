#!/usr/bin/env python3
"""ML-assisted step: propose segment boundaries with PySceneDetect and compare to manual labels.

For every registered clip it
  1. detects shot cuts (ContentDetector),
  2. writes proposals to data/proposals/<clip_id>.json (use them as a starting point in the annotator),
  3. measures how often a manual *delivery* start/end lies within --tol seconds of an automatic cut
     (broadcast footage usually cuts to/from the bowler's-end camera around each ball),
     and how many automatic cuts are not near any manual boundary.

Usage:
  python scripts/auto_segment.py --annotator main --tol 1.0 --threshold 27
"""
import argparse
import json
from pathlib import Path

from scenedetect import ContentDetector, detect

from common import CLIPS_DIR, REPORTS_DIR, ROOT, load_annotations, load_provenance


def near(t, cuts, tol):
    return any(abs(t - c) <= tol for c in cuts)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--annotator", default="main")
    ap.add_argument("--tol", type=float, default=1.0)
    ap.add_argument("--threshold", type=float, default=27.0, help="ContentDetector threshold (lower = more cuts)")
    ap.add_argument("--report", type=Path, default=REPORTS_DIR / "auto_vs_manual.md")
    a = ap.parse_args()

    prov = load_provenance()
    manual = {d["clip_id"]: d for _, _, d, e in load_annotations(a.annotator) if d}
    prop_dir = ROOT / "data" / "proposals"
    prop_dir.mkdir(parents=True, exist_ok=True)

    rows, tot_b, tot_hit, tot_cuts, tot_cuts_near = [], 0, 0, 0, 0
    for cid, row in prov.items():
        clip = CLIPS_DIR / row["filename"]
        if not clip.is_file():
            print(f"skip {cid}: clip file not found")
            continue
        scenes = detect(str(clip), ContentDetector(threshold=a.threshold))
        cuts = [round(getattr(s[0], 'seconds', None) or s[0].get_seconds(), 3) for s in scenes[1:]]  # start of every scene but the first
        (prop_dir / f"{cid}.json").write_text(json.dumps({
            "clip_id": cid, "method": f"scenedetect.ContentDetector(threshold={a.threshold})",
            "proposed_cut_times_s": cuts}, indent=2), encoding="utf-8")

        bounds = []
        if cid in manual:
            for e in manual[cid]["events"]:
                if e["type"] == "delivery":
                    bounds += [e["start_s"], e["end_s"]]
        hit = sum(near(b, cuts, a.tol) for b in bounds)
        cuts_near = sum(near(c, bounds, a.tol) for c in cuts)
        rows.append((cid, len(cuts), len(bounds), hit, cuts_near))
        tot_b += len(bounds); tot_hit += hit; tot_cuts += len(cuts); tot_cuts_near += cuts_near

    recall = tot_hit / tot_b if tot_b else float("nan")
    prec = tot_cuts_near / tot_cuts if tot_cuts else float("nan")
    md = [
        "# Automatic cuts vs manual delivery boundaries", "",
        f"Detector: PySceneDetect ContentDetector (threshold {a.threshold}); tolerance {a.tol}s.", "",
        f"- Manual delivery boundaries with an automatic cut nearby: **{tot_hit}/{tot_b}** "
        f"({'n/a' if recall != recall else f'{recall:.0%}'})",
        f"- Automatic cuts that sit near a manual boundary: **{tot_cuts_near}/{tot_cuts}** "
        f"({'n/a' if prec != prec else f'{prec:.0%}'})", "",
        "| clip | auto cuts | manual boundaries | boundaries matched | cuts near a boundary |", "|---|---|---|---|---|",
        *(f"| {c} | {n} | {b} | {h} | {cn} |" for c, n, b, h, cn in rows), "",
        "Reading it: low recall means deliveries are not separated by camera cuts (e.g. a single-camera "
        "nets clip) so manual segmentation is essential; low precision means many cuts are replays/crowd shots "
        "that are not delivery boundaries. Both findings are worth a sentence in your dataset card.", "",
    ]
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
