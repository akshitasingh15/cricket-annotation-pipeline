# Draft answer for the form (edit so it sounds like you and so every claim is true)

**If we give you 1,000 cricket or football clips, how would you collect, structure, annotate and QA them so an AI/CV engineer can reliably use the dataset?**

I would start by agreeing the use case with the engineer (what the model must predict), then freeze a versioned label schema and a written annotation guideline. For collection, every clip gets a manifest row: source URL, licence, date, SHA-256; duplicates and unlicensed footage are rejected. For structure, I use stable clip IDs, one folder layout, and a JSON schema that enforces required fields and consistent labels (event type, start/end time, outcome, confidence).

I would annotate in rounds: a pilot of about 50 clips by two annotators to find ambiguous rules and fix the guideline, then production with scene-detection pre-filling boundaries, and 10-15% of clips double-annotated. For QA, scripts check schema validity, overlapping or out-of-order events, events past the clip end and missing annotations on every commit. I measure event F1 and Cohen's kappa per class, and re-review low-confidence labels and low-kappa classes. I release with a dataset card (counts, class balance, limitations, licences) and train/validation/test splits made by match or source, not by clip, so the engineer does not get leakage.

I built a small cricket version of this: [GitHub link]. It has provenance tracking, a keyboard annotation tool, QA scripts and an agreement check on [N] clips.

_Only keep the last paragraph's numbers after you've actually measured them._
