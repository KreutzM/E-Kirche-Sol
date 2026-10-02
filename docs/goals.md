# Three long Goals for the exterior reconstruction

## Quality contract

User clarification, 2026-10-02: the finished 3D exterior should look convincing;
centimetre accuracy is not required. Preserve the independent experiment, metre
units, coordinates, evidence precedence and explicit assumptions in `AGENTS.md`.
Approximate camera fitting and simplified small ornaments are acceptable if labeled.
Do not pursue precision that does not materially improve visible quality.

The issue audit found that #2–#8 covered evidence, massing, cameras and reporting,
but omitted architectural detail, materials and final model delivery. They are now
organised into three executable Goals, with #3–#7 as sub-issues inside Goal 1.
Do not run a separate Goal for every sub-issue. Goal 2 supplies the missing exterior
detail/material work. Goal 3 includes final corrections and delivery, not just prose.

| Order | Parent issue | Result | Dependencies |
| --- | --- | --- | --- |
| 1 | [#2](https://github.com/KreutzM/E-Kirche-Sol/issues/2) | Evidence-backed complete coarse exterior and repeatable comparison views | None |
| 2 | [#9](https://github.com/KreutzM/E-Kirche-Sol/issues/9) | Complete visually developed exterior | #2 |
| 3 | [#8](https://github.com/KreutzM/E-Kirche-Sol/issues/8) | Visually verified final model, reproducible delivery and SOL-01 report | #2 and #9 |

Each parent issue contains a ready-to-use `/goal` start text. Start them in the
order #2, #9, #8. No Goal is active merely because these issues have been prepared.

## Goal 1 — evidence and complete coarse exterior

Verify the 32 manifest records against their original public sources, retaining
licence/provenance records. Download useful Priority-1 references and inspect
contact sheets and individual relevant images. Record failures and coverage gaps;
acquire additional open references only when a consequential gap requires them.
A broken redundant reference does not block modeling if the remaining evidence is
sufficient. Unlicensed evidence must not be downloaded or redistributed.

Complete #3 (acquisition), #4 (footprint/scale), #5 (nave/transept/triconch),
#6 (westwork/towers/roofs) and #7 (initial validation cameras) in a single loop.
Include visibly significant annexes such as the sacristy in coarse form. Read the
required project evidence before modeling and follow the coarse-to-fine order.

Done when a reproducible generator saves the complete coarse exterior to
`blender/scene/elisabethkirche.blend`, assumptions and scale checks are current,
and W/SW/S/SE/N comparison renders plus an elevated roof view and plan/elevation
views exist. Use best available valid evidence for each view. Record camera fitting
and limitations; an approximate fit is sufficient. Document the massing review in
`validation/reports/goal-1.md`. Silhouette/proportions/roof form must each reach
at least level 2 below, without known gross errors in tower count, major volumes,
orientation or roof topology. A skeleton or scale-guide scene is insufficient.

## Goal 2 — architecture and materials

Start from accepted Goal-1 massing. Build characteristic buttresses, openings,
window recesses and visible glazing/tracery, west portal and facade, tower stages,
spires, roof transitions, sacristy details and visually important ornament. Use
parametric repetition where practical; give inferred dimensions stable assumption
keys, including reused dimensions. Avoid unsupported ornate invention.

Create credible stone, slate/roof, glazing and metal materials at architectural
scale. Prioritise visible facade rhythm, depth and recognisable features over
subpixel sculpture. Model small details economically at the intended viewing scale.
Refine coarse geometry if multiple views reveal a problem.

Done when the whole exterior is developed, saved and reproducible, the five
principal comparisons and elevated view are updated, and silhouette/proportions,
roof forms, facade rhythm, distinctive architecture and materials each reach
level 3. Record the per-view assessment and remaining minor uncertainties in
`validation/reports/goal-2.md`. Attractive lighting cannot compensate for a
known structural error. There must be no visibly unfinished major facade/roof.

## Goal 3 — final quality and delivery

Review all sides under neutral lighting, fix remaining conspicuous defects and
verify details do not degrade accepted massing. Include plan/elevation and an
elevated roof check. Reuse documented validation cameras; changes require an
evidence-based reason. Presentation cameras are separate and clearly labeled.

Done when all visual categories reach level 3 across supported views, there are
no conspicuous floating/intersecting pieces, unintended holes, missing major
elements or visibly inconsistent material scale at normal viewing distance,
and the saved `.blend` reopens correctly. Simplified or evidence-poor areas are
identified explicitly; a hidden side is not exempt from coherent modeling.

Deliver the `.blend`, one usable GLB export, at least five principal neutral
renders and two presentation renders (suggested 1600 px or larger), and
`validation/reports/SOL-01.md` with links/paths to the artifacts, evidence,
assumptions, per-view findings, limitations, reproducibility and human intervention.
Include a single documented build command that regenerates model, cameras,
materials, renders and export from a clean scene. Check the GLB opens/imports
with plausible bounds, object content and materials. Retain distributed asset
attributions/licences. Commit code/reports and deliver binaries through Git LFS
or clearly documented accessible artifacts; verify delivery rather than merely
creating ignored local files. Push where authorised. Keep final render evidence
reviewable in the repository or explicitly linked artifacts.

Freeze the independent Sol result with a commit identifier. Comparing with the
excluded sibling experiment is outside these Goals and requires separate user
instruction after freezing; #8 no longer implies permission for that comparison.

## Visual acceptance rubric

Assess silhouette/proportions, roof forms, facade rhythm/openings, distinctive
architecture and materials under neutral lighting. Record a score per category
and view, the evidence IDs, observed discrepancies and intended fixes. The score
is a documented visual judgment, not a measured accuracy claim.

- 0: absent or unusable.
- 1: conspicuously wrong or unfinished at normal viewing distance.
- 2: coherent and recognisable; visible deviations still warrant refinement.
- 3: convincing at normal viewing distance; remaining differences are minor or
  explicitly uncertain and do not undermine the building's character.

Use W (M10/M11), SW (M09), S (M04/M05), SE (M02/M03/M19) and N (M06/M07),
with M01 for roof form and P01/P02/P06/P07/P08 for structural cross-checks.
Historical sources require modern-condition caveats. M08 is excluded from normal
pinhole calibration unless its projection is explicitly established; its existing
`do_not_camera_solve` manifest classification suffices without invented metadata.
Record unavailable views and replacement evidence. Evidence-poor details may be
coherent approximations; missing references must never be claimed as agreement.

## Continuation and verification

Maintain `docs/progress.md` during execution: active Goal, completed sub-issues,
latest commands/artifacts, current commit, known defects, next highest-impact
action and any external blocker. Update it at meaningful checkpoints so a long
Goal can continue from disk after context changes. Keep work going through internal
milestones; stop only at the Goal's actual finish line or a genuine blocker.
Choose the next change by visible impact and evidence confidence.

After material geometry changes run dataset validation, regenerate relevant
renders, inspect comparisons and update assumptions/discrepancies. At delivery
also run pipeline tests and a fresh Blender build with `--python-exit-code 1`.
No exact reprojection residual or centimetre threshold is required. Missing
optional references or unresolved tiny ornaments do not warrant endless refinement.
Report an external blocker with attempts, fallback evidence, saved progress and
the input needed to proceed; ordinary modeling uncertainty is handled by documented
assumptions. Follow the Goal lifecycle supplied by the environment.

The outcome/verification/constraints structure follows
[official OpenAI guidance on Goals](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex).
Preparing these issues does not start a reconstruction Goal.
