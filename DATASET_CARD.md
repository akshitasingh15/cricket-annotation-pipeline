# Dataset card: Cricket event annotation set

**Schema version:** 1.0.0  **Annotator:** `main`

## Size
- Clips: **5** (39 s total, mean 8 s)
- Annotated clips: **5**
- Events: **9**

## Event type distribution
| type | count |
|---|---|
| shot | 5 |
| delivery | 3 |
| boundary | 1 |

## Shot types
| shot_type | count |
|---|---|
| slog | 3 |
| leave | 1 |
| sweep | 1 |

## Delivery outcomes
| outcome | count |
|---|---|
| dot | 1 |
| runs | 1 |
| boundary | 1 |

## Dismissals
| dismissal | count |
|---|---|
| - | 0 |

## Label confidence
| confidence | count |
|---|---|
| high | 9 |

## Provenance
| source platform | clips |
|---|---|
| pexels | 4 |
| Pexels | 1 |

| licence | clips |
|---|---|
| Pexels License | 1 |
| https://www.pexels.com/video/cricketer-practicing-batting-on-sunny-day-32543231/ | 1 |
| https://www.pexels.com/video/intense-cricket-match-in-action-on-field-36088033/ | 1 |
| https://www.pexels.com/video/competitive-cricket-match-on-sunny-day-36088036/ | 1 |
| https://www.pexels.com/video/exciting-cricket-match-in-urban-playground-35550704/ | 1 |

Every clip has a source URL (or is self-recorded), licence, collection date and SHA-256 in `data/provenance.csv`.
Raw video is not redistributed in this repository.

## Known limitations
_Fill these in honestly. Examples: small sample; mostly one camera angle; class imbalance (few wickets);
single primary annotator, agreement measured on N clips only; no ball-tracking labels._

## Intended use
Prototype event-segmentation and shot-classification experiments; not a benchmark.
