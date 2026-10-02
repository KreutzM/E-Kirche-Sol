# Decision log

## 2026-10-02 — Independent GPT-6.1-Sol experiment

Decision: create a separate repository for the Sol attempt.

Reason: avoid cross-contamination from the earlier reconstruction and permit a meaningful comparison.

## 2026-10-02 — Same evidence class, clean solution state

Decision: reuse the original curated source manifest, documented scale anchors and neutral pipeline scaffolding, but not any later model-specific outputs or inferred dimensions.

## 2026-10-02 — Exterior-only scope

Decision: reconstruct the exterior before considering the interior.

## 2026-10-02 — Script-first Blender workflow

Decision: repeated and structural geometry should be generated or parameterised with Blender Python where practical.

## 2026-10-02 — Repository readiness audit

Decision: strengthen offline checks for dimensions, source IDs, assumptions,
reference-view evidence and the complete coordinate convention; run regression
checks on Windows and Linux. Preserve reference downloads and append provenance
instead of resetting it on each run. Reject restricted CC licence variants and
return a failing exit status for download errors.

Blender output paths now follow script locations. The neutral hall-width guide
was corrected to Y, transverse to the X-directed hall, using the existing 21.55 m
documented interior anchor. This remains a hidden scale guide; no exterior geometry
or inferred dimensions were created. See `development.md` for the audit, local
commands and remaining acquisition/visual-validation work.

## 2026-10-02 — Three Goals and visual acceptance

User clarification: the finished exterior should be optically convincing;
centimetre accuracy is not required. Keep the established metric/evidence rules,
but focus effort on visible proportions, architecture, roofs and materials.

Decision: make #2 the complete evidence-to-massing Goal (including #3–#7), add
#9 for architectural exterior/material work, and expand #8 to final refinement,
verified artifact delivery and the independent SOL-01 report. Camera fitting may
be approximate and should begin during massing. A sibling-experiment comparison
is excluded from these Goals, even after freezing, unless separately requested.

The three parent issues now define dependencies, deliverables, visual acceptance
and copyable `/goal` prompts. `goals.md` records the shared contract and
`progress.md` provides the initial continuation checkpoint. Issue preparation
does not mark any modeling work complete or start a reconstruction Goal.
