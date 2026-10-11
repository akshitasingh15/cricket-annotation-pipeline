# Automatic cuts vs manual delivery boundaries

Detector: PySceneDetect ContentDetector (threshold 27.0); tolerance 1.0s.

- Manual delivery boundaries with an automatic cut nearby: **0/6** (0%)
- Automatic cuts that sit near a manual boundary: **0/0** (n/a)

| clip | auto cuts | manual boundaries | boundaries matched | cuts near a boundary |
|---|---|---|---|---|
| net_session_01 | 0 | 0 | 0 | 0 |
| practice_01 | 0 | 0 | 0 | 0 |
| practice_03 | 0 | 2 | 0 | 0 |
| practice_04 | 0 | 2 | 0 | 0 |
| practice_02 | 0 | 2 | 0 | 0 |

Reading it: low recall means deliveries are not separated by camera cuts (e.g. a single-camera nets clip) so manual segmentation is essential; low precision means many cuts are replays/crowd shots that are not delivery boundaries. Both findings are worth a sentence in your dataset card.
