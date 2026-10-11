# Where to find cricket videos you are allowed to use

The role lists **provenance** as a requirement, so where a clip comes from matters as much as the labels.
Rule of thumb: use only footage that is yours, or whose licence you can quote. Log it with `register_clip.py`.

## Best: record it yourself (strongest signal for the role)
* Nets sessions, college or local-club matches, a friend's backyard game. 15-60 s per clip, phone held steady.
* Get verbal/written permission from the players, coach or ground owner, and say you are using the clips for an annotation project.
* Tips: film from behind the bowler's arm, side-on, or from the stands; 1080p, 30 fps; avoid zoom changes; record a few full deliveries per clip.
* Register with `--platform self_recorded --licence "Own work"`.
* 6-8 of these plus the clips below is a good dataset.

## Licensed / open sources
| Source | What to look for | Licence note |
|---|---|---|
| **Pexels Videos** (pexels.com/videos) | Search "cricket", "batsman", "bowler", "cricket match" | Pexels licence allows free use and modification; you may not sell unaltered copies or redistribute on other stock platforms. Verified at pexels.com/license. Do not commit the raw files to your repo; commit provenance and annotations only. |
| **Wikimedia Commons** (commons.wikimedia.org, `Category:Cricket` and its sub-categories) | Video files (.webm, .ogv) inside cricket categories | Each file has its own licence (CC BY, CC BY-SA, public domain). Copy the licence and author from the file page; CC BY requires attribution. |
| **Pixabay Videos** (pixabay.com/videos) | Search "cricket" | Check the licence on the page of each video before use and record it. |
| **Internet Archive** (archive.org) | Search "cricket"; filter by licence or public domain, usually old newsreels | Every item has a licence/rights field; quote it. Old black-and-white footage is useful for variety but not for modern shot types. |
| **YouTube, Creative Commons filter** | Search → Filters → Features → *Creative Commons* | The uploader may mislabel footage they do not own (broadcast clips are often wrongly marked CC). YouTube's terms also restrict downloading unless a download option is offered. Prefer the sources above, or ask the uploader for permission. |

## Do not use
* IPL, ICC, BCCI, county or any broadcaster footage, or clips ripped from Instagram, Facebook, X or TikTok. These are copyrighted. Using them in a portfolio project can get a repo taken down and looks bad to a data-focused employer.

## Reality check on stock footage
Stock clips are often staged or highlight-style: few full deliveries, many camera cuts. They are good for variety and for testing the scene-detection step, but your own clips will give you more real deliveries, shots and outcomes to annotate. Say so in the dataset card's limitations.

## What to record for each clip (the script does most of it)
Source platform, page URL, author, licence name and URL, date collected, SHA-256, duration, resolution, frame rate. `scripts/register_clip.py` fills the last five automatically.
