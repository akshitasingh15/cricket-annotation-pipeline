# Annotation guidelines (v1.0.0)

Goal: two people labelling the same clip should produce the same events within ~1 second and with the same labels.
If you hit a case not covered here, label your best guess with `confidence: low`, add a note, and later add the rule to this file (bump the version).

## General rules
* Times are seconds from the start of the clip, 3 decimals. Use the frame-step keys (`,` `.`) for precision.
* Events are sorted by `start_s`. Events of the same type must not overlap (except `shot` and `fielding`, which may sit inside a delivery).
* `confidence`: **high** = clearly visible; **medium** = visible but ambiguous (camera angle, occlusion); **low** = you are guessing. Low-confidence labels are reviewed.
* Label only what you can see in this clip. Do not use commentary, scoreboard or outside knowledge to decide.
* Replays: do **not** annotate replays as new events. Annotate only the live action.

## Event types

### delivery (key 1)
One ball bowled.
* **start**: first frame the bowler begins the run-up (or, for a clip that starts mid-run-up, the first frame of the clip).
* **end**: ball is dead: in the keeper's/bowler's hands after the play, or the final fielding action of that ball.
* `bowler_type`: `pace` (run-up longer than ~8 steps and fast arm) / `spin` / `unknown`.
* `length` (where it pitches): `yorker` (at the feet), `full`, `good`, `short`, `unknown`.
* `outcome`: `dot`, `runs` (1-3 run(s), no boundary), `boundary`, `wicket`, `extra`, `unknown`.
* Must be consistent with the events inside it (see QA rules: outcome `wicket` requires a `wicket` event, etc.).

### shot (key 2)
A batter's attempt to hit or defend the ball.
* **start**: first frame of the forward swing / defensive movement (not the stance).
* **end**: 0.3 s after ball contact, or after the bat has passed the ball for a miss.
* `shot_type`: `drive`, `cut`, `pull`, `hook`, `sweep`, `flick`, `glance`, `defence`, `leave`, `slog`, `other`. If it is not clearly one of these, use `other`.
* `contact`: `middled`, `edged`, `mistimed`, `missed`, `none` (use `none` for a leave).

### boundary (key 3)
Ball reaches or crosses the rope.
* **start**: first frame after the ball leaves the bat. **end**: ball crosses/touches the rope.
* `runs`: `6` if the ball crosses the rope without bouncing, else `4`.

### wicket (key 4)
A dismissal.
* **start**: the moment the dismissal happens (stumps hit, catch completed, bails off, run-out broken). **end**: 1.0 s later or when the batter starts walking, whichever is first.
* `dismissal`: `bowled`, `caught`, `lbw`, `run_out`, `stumped`, `hit_wicket`, `other`. If the review result is not visible in the clip, label what the on-field action shows and set confidence to `medium`.

### appeal (key 5)
Fielding side appeals to the umpire.
* **start**: first frame of the appeal (raised arms/shout). **end**: umpire's decision signal, or 2 s after start if no decision is visible.
* `result`: `out`, `not_out`, `review`, `unknown`.

### extra (key 6)
* **start**: ball release. **end**: umpire's signal, or when the ball is dead if no signal is visible.
* `extra_type`: `wide`, `no_ball`, `bye`, `leg_bye`.

### fielding (key 7)
Notable fielding action.
* **start**: fielder's first movement toward the ball. **end**: ball in hand, dropped, or thrown.
* `action`: `catch`, `drop`, `stop`, `throw`, `misfield`.

## Edge cases
* Several deliveries in one clip: one `delivery` event each; shots/boundaries/wickets belong inside the matching delivery span.
* Clip starts or ends mid-delivery: annotate the visible part; note `clip cut` in `notes`.
* No-ball with a wicket-style event: the `delivery` outcome is `extra`; do not label a `wicket` unless the batter is actually dismissed (e.g. run-out).
* Nets sessions: no umpire, so `appeal` and `extra` normally do not apply.

## Process
1. Read this file. 2. Annotate a pilot of 3 clips, discuss disagreements with the second annotator, update the guideline. 3. Annotate the rest. 4. Run `scripts/validate.py` and fix everything. 5. Second annotator labels at least 5 clips blind. 6. Run `scripts/agreement.py`.

## Changelog
* 1.0.0 - initial version.
