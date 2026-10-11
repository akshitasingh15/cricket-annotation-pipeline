#!/usr/bin/env python3
"""Inter-annotator agreement between two annotators on the clips both have labelled.

Three views of agreement:
  1. Event detection  - events of the same type whose start times are within --tol seconds are
                        matched (greedy, closest first). Reports precision / recall / F1 of B vs A
                        and the mean absolute start-time offset of matched pairs.
  2. Attribute kappa  - for matched pairs, Cohen's kappa on the main label of each event type
                        (shot_type, dismissal, delivery outcome, ...).
  3. Time-bin kappa   - the clip is cut into --bin second bins; each bin gets the highest-priority
                        event type active in it (or 'none'); Cohen's kappa between annotators.

Usage:
  python scripts/agreement.py --a main --b friend --tol 1.0 --bin 0.5
"""
import argparse
from collections import Counter, defaultdict
from pathlib import Path

from common import ANNOTATIONS_DIR, REPORTS_DIR, load_annotations, load_provenance

ATTR = {  # main label per event type
    "delivery": "outcome", "shot": "shot_type", "boundary": "runs", "wicket": "dismissal",
    "appeal": "result", "extra": "extra_type", "fielding": "action",
}
PRIORITY = ["wicket", "boundary", "appeal", "extra", "fielding", "shot", "delivery"]


def cohen_kappa(a: list, b: list) -> float:
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    if pe == 1:
        return 1.0 if po == 1 else 0.0
    return (po - pe) / (1 - pe)


def match_events(ea, eb, tol):
    """Greedy one-to-one matching of same-type events by |start difference| <= tol."""
    pairs = []
    for i, x in enumerate(ea):
        for j, y in enumerate(eb):
            if x["type"] == y["type"] and abs(x["start_s"] - y["start_s"]) <= tol:
                pairs.append((abs(x["start_s"] - y["start_s"]), i, j))
    pairs.sort()
    used_a, used_b, out = set(), set(), []
    for d, i, j in pairs:
        if i in used_a or j in used_b:
            continue
        used_a.add(i)
        used_b.add(j)
        out.append((ea[i], eb[j], d))
    return out


def bin_labels(events, duration, width):
    n = max(1, int(duration / width + 0.9999))
    labels = ["none"] * n
    rank = {t: i for i, t in enumerate(PRIORITY)}
    for e in events:
        lo = int(e["start_s"] / width)
        hi = int(max(e["end_s"] - 1e-9, e["start_s"]) / width)
        for k in range(lo, min(hi, n - 1) + 1):
            cur = labels[k]
            if cur == "none" or rank[e["type"]] < rank[cur]:
                labels[k] = e["type"]
    return labels


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--a", required=True, help="reference annotator folder name, e.g. main")
    ap.add_argument("--b", required=True, help="second annotator folder name, e.g. friend")
    ap.add_argument("--tol", type=float, default=1.0, help="start-time tolerance in seconds")
    ap.add_argument("--bin", type=float, default=0.5, help="bin width in seconds for time-bin kappa")
    ap.add_argument("--report", type=Path, default=REPORTS_DIR / "agreement_report.md")
    args = ap.parse_args()

    A = {d["clip_id"]: d for _, _, d, e in load_annotations(args.a) if d}
    B = {d["clip_id"]: d for _, _, d, e in load_annotations(args.b) if d}
    shared = sorted(set(A) & set(B))
    if not shared:
        raise SystemExit(f"No clips annotated by both '{args.a}' and '{args.b}'.")
    prov = load_provenance()

    tp = Counter(); fn = Counter(); fp = Counter()
    offsets = []
    attr_pairs = defaultdict(lambda: ([], []))
    bins_a, bins_b = [], []
    for cid in shared:
        ea, eb = A[cid]["events"], B[cid]["events"]
        m = match_events(ea, eb, args.tol)
        matched_a = {id(x) for x, _, _ in m}
        matched_b = {id(y) for _, y, _ in m}
        for x, y, d in m:
            tp[x["type"]] += 1
            offsets.append(d)
            key = ATTR[x["type"]]
            attr_pairs[x["type"]][0].append(str(x.get(key)))
            attr_pairs[x["type"]][1].append(str(y.get(key)))
        for x in ea:
            if id(x) not in matched_a:
                fn[x["type"]] += 1
        for y in eb:
            if id(y) not in matched_b:
                fp[y["type"]] += 1
        dur = float(prov.get(cid, {}).get("duration_s") or 0) or max(
            [e["end_s"] for e in ea + eb] + [args.bin])
        bins_a += bin_labels(ea, dur, args.bin)
        bins_b += bin_labels(eb, dur, args.bin)

    def prf(t, f_p, f_n):
        p = t / (t + f_p) if t + f_p else float("nan")
        r = t / (t + f_n) if t + f_n else float("nan")
        f = 2 * p * r / (p + r) if p == p and r == r and p + r else float("nan")
        return p, r, f

    types = [t for t in PRIORITY if tp[t] + fp[t] + fn[t]]
    rows = []
    for t in types:
        p, r, f = prf(tp[t], fp[t], fn[t])
        k = cohen_kappa(*attr_pairs[t]) if tp[t] else float("nan")
        raw = (sum(x == y for x, y in zip(*attr_pairs[t])) / tp[t]) if tp[t] else float("nan")
        rows.append((t, tp[t], fp[t], fn[t], p, r, f, raw, k))
    TP, FP, FN = sum(tp.values()), sum(fp.values()), sum(fn.values())
    P, R, F = prf(TP, FP, FN)
    bin_k = cohen_kappa(bins_a, bins_b)
    bin_raw = sum(x == y for x, y in zip(bins_a, bins_b)) / len(bins_a)
    mean_off = sum(offsets) / len(offsets) if offsets else float("nan")

    def f2(x):
        return "n/a" if x != x else f"{x:.2f}"

    md = [
        f"# Inter-annotator agreement: `{args.a}` vs `{args.b}`", "",
        f"- Clips annotated by both: **{len(shared)}**  (tolerance {args.tol}s, bin {args.bin}s)",
        f"- Event detection overall: precision {f2(P)}, recall {f2(R)}, **F1 {f2(F)}** (reference = `{args.a}`)",
        f"- Mean |start offset| of matched events: {f2(mean_off)}s",
        f"- Time-bin agreement: raw {f2(bin_raw)}, **Cohen's kappa {f2(bin_k)}**", "",
        "| event type | matched | extra in B | missed by B | precision | recall | F1 | label agreement | label kappa |",
        "|---|---|---|---|---|---|---|---|---|",
        *(f"| {t} | {a_} | {b_} | {c_} | {f2(p)} | {f2(r)} | {f2(f)} | {f2(raw)} | {f2(k)} |"
          for t, a_, b_, c_, p, r, f, raw, k in rows),
        "", "Note: label kappa from only a handful of matched events is unstable - quote it only with 30+ matched "
        "pairs per class, otherwise report raw agreement and say how small the sample is.", "",
        "Interpretation (Landis & Koch): <0.20 slight, 0.21-0.40 fair, 0.41-0.60 moderate, "
        "0.61-0.80 substantial, >0.80 almost perfect. Low-kappa classes usually mean the guideline "
        "for that class is ambiguous - fix the guideline, bump the schema version, re-annotate.", "",
    ]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    print(f"Report written to {args.report}")


if __name__ == "__main__":
    main()
