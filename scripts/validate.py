#!/usr/bin/env python3
"""QA checks for the dataset. Exits non-zero if any ERROR is found.

Checks
  provenance : required fields present, sha256 format, duplicate hashes, clip file exists + hash matches
  schema     : every annotation file validates against schema/event_schema.json
  logic      : start < end, end <= clip duration, events sorted, no overlapping events of the
               same type (except shots/fielding which may overlap a delivery), unique event ids,
               boundary/wicket must sit inside a delivery, delivery outcome consistent with child events
  coverage   : clips without any annotation, annotation files with no registered clip, empty annotations

Writes reports/qa_report.md
"""
import argparse
import sys
from collections import defaultdict
from pathlib import Path

from jsonschema import Draft202012Validator

from common import (ANNOTATIONS_DIR, CLIPS_DIR, REPORTS_DIR, REQUIRED_PROVENANCE, load_annotations,
                    load_provenance, load_schema, sha256_file)

TOL = 0.05  # seconds of float slack


def check_provenance(prov, errors, warnings, verify_hash):
    seen = {}
    for cid, row in prov.items():
        for field in REQUIRED_PROVENANCE:
            if not (row.get(field) or "").strip():
                errors.append(f"[provenance] {cid}: missing '{field}'")
        sha = row.get("sha256", "")
        if sha and len(sha) != 64:
            errors.append(f"[provenance] {cid}: sha256 is not 64 hex chars")
        if sha in seen:
            errors.append(f"[provenance] {cid}: duplicate content of {seen[sha]}")
        seen[sha] = cid
        if row.get("source_platform") != "self_recorded" and not (row.get("source_url") or "").strip():
            warnings.append(f"[provenance] {cid}: no source_url for a non-self-recorded clip")
        clip_file = CLIPS_DIR / (row.get("filename") or "")
        if clip_file.is_file() and verify_hash and sha256_file(clip_file) != sha:
            errors.append(f"[provenance] {cid}: file hash differs from recorded sha256 (file changed?)")
        elif not clip_file.is_file():
            warnings.append(f"[provenance] {cid}: clip file not found locally ({row.get('filename')}); hash not verified")


def check_events(cid, who, data, duration, errors, warnings):
    tag = f"[logic] {who}/{cid}"
    events = data["events"]
    ids = [e["id"] for e in events]
    if len(ids) != len(set(ids)):
        errors.append(f"{tag}: duplicate event ids")
    if not events:
        warnings.append(f"{tag}: annotation file has zero events")
    prev_start = -1.0
    for e in events:
        label = f"event #{e['id']} ({e['type']})"
        if e["end_s"] < e["start_s"] - TOL:
            errors.append(f"{tag}: {label} end_s < start_s")
        if duration and e["end_s"] > duration + TOL:
            errors.append(f"{tag}: {label} end_s {e['end_s']:.2f} beyond clip duration {duration:.2f}")
        if e["start_s"] < prev_start - TOL:
            errors.append(f"{tag}: {label} out of order (events must be sorted by start_s)")
        prev_start = max(prev_start, e["start_s"])
        if e["confidence"] == "low":
            warnings.append(f"{tag}: {label} flagged low confidence - re-check")

    by_type = defaultdict(list)
    for e in events:
        by_type[e["type"]].append(e)
    for etype, evs in by_type.items():
        if etype in ("shot", "fielding"):
            continue
        evs = sorted(evs, key=lambda x: x["start_s"])
        for a, b in zip(evs, evs[1:]):
            if b["start_s"] < a["end_s"] - TOL:
                errors.append(f"{tag}: overlapping {etype} events #{a['id']} and #{b['id']}")

    deliveries = by_type.get("delivery", [])

    def inside_delivery(e):
        return any(d["start_s"] - TOL <= e["start_s"] and e["end_s"] <= d["end_s"] + TOL for d in deliveries)

    for e in events:
        if e["type"] in ("boundary", "wicket", "shot", "extra") and deliveries and not inside_delivery(e):
            warnings.append(f"{tag}: {e['type']} #{e['id']} is not inside any delivery span")

    for d in deliveries:
        kids = [e for e in events if e is not d and d["start_s"] - TOL <= e["start_s"] and e["end_s"] <= d["end_s"] + TOL]
        kinds = {k["type"] for k in kids}
        if d["outcome"] == "boundary" and "boundary" not in kinds:
            errors.append(f"{tag}: delivery #{d['id']} outcome=boundary but no boundary event inside it")
        if d["outcome"] == "wicket" and "wicket" not in kinds:
            errors.append(f"{tag}: delivery #{d['id']} outcome=wicket but no wicket event inside it")
        if d["outcome"] == "extra" and "extra" not in kinds:
            errors.append(f"{tag}: delivery #{d['id']} outcome=extra but no extra event inside it")
        if "wicket" in kinds and d["outcome"] != "wicket":
            errors.append(f"{tag}: delivery #{d['id']} contains a wicket but outcome={d['outcome']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--annotations", type=Path, default=ANNOTATIONS_DIR)
    ap.add_argument("--no-hash-check", action="store_true", help="skip re-hashing clip files")
    ap.add_argument("--report", type=Path, default=REPORTS_DIR / "qa_report.md")
    a = ap.parse_args()

    errors, warnings = [], []
    prov = load_provenance()
    check_provenance(prov, errors, warnings, not a.no_hash_check)

    validator = Draft202012Validator(load_schema())
    annotated = defaultdict(set)
    n_files = n_events = 0
    for who, path, data, err in load_annotations(root=a.annotations):
        n_files += 1
        if err:
            errors.append(f"[schema] {who}/{path.name}: invalid JSON ({err})")
            continue
        problems = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
        for p in problems:
            loc = "/".join(str(x) for x in p.absolute_path) or "(root)"
            errors.append(f"[schema] {who}/{path.name} at {loc}: {p.message[:160]}")
        if problems:
            continue
        cid = data["clip_id"]
        if cid != path.stem:
            errors.append(f"[schema] {who}/{path.name}: clip_id '{cid}' does not match filename")
        if data["annotator"] != who:
            errors.append(f"[schema] {who}/{path.name}: annotator '{data['annotator']}' does not match folder")
        if cid not in prov:
            errors.append(f"[coverage] {who}/{path.name}: clip '{cid}' is not in provenance.csv")
            duration = 0
        else:
            duration = float(prov[cid]["duration_s"] or 0)
        annotated[cid].add(who)
        n_events += len(data["events"])
        check_events(cid, who, data, duration, errors, warnings)

    for cid in prov:
        if cid not in annotated:
            errors.append(f"[coverage] {cid}: registered clip has no annotation")

    a.report.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# QA report", "",
        f"- Registered clips: **{len(prov)}**",
        f"- Annotation files: **{n_files}** ({n_events} events)",
        f"- Errors: **{len(errors)}**   Warnings: **{len(warnings)}**", "",
        "## Errors", "", *(f"- {e}" for e in errors or ["none"]), "",
        "## Warnings", "", *(f"- {w}" for w in warnings or ["none"]), "",
    ]
    a.report.write_text("\n".join(lines), encoding="utf-8")

    for e in errors:
        print("ERROR  ", e)
    for w in warnings:
        print("WARN   ", w)
    print(f"\n{len(prov)} clips, {n_files} annotation files, {n_events} events -> {len(errors)} errors, {len(warnings)} warnings")
    print(f"Report written to {a.report}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
