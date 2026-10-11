# Inter-annotator agreement: `main` vs `1`

- Clips annotated by both: **1**  (tolerance 1.0s, bin 0.5s)
- Event detection overall: precision 1.00, recall 1.00, **F1 1.00** (reference = `main`)
- Mean |start offset| of matched events: 0.00s
- Time-bin agreement: raw 1.00, **Cohen's kappa 1.00**

| event type | matched | extra in B | missed by B | precision | recall | F1 | label agreement | label kappa |
|---|---|---|---|---|---|---|---|---|
| shot | 1 | 0 | 0 | 1.00 | 1.00 | 1.00 | 0.00 | 0.00 |

Note: label kappa from only a handful of matched events is unstable - quote it only with 30+ matched pairs per class, otherwise report raw agreement and say how small the sample is.

Interpretation (Landis & Koch): <0.20 slight, 0.21-0.40 fair, 0.41-0.60 moderate, 0.61-0.80 substantial, >0.80 almost perfect. Low-kappa classes usually mean the guideline for that class is ambiguous - fix the guideline, bump the schema version, re-annotate.
