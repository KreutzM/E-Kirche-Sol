# GPT-6.1-Sol — Elisabethkirche Marburg Reconstruction

## Mission

Reconstruct the **present-day EXTERIOR only** of the Elisabethkirche in Marburg as a metrically coherent, auditable Blender model.

This is an independent GPT-6.1-Sol experiment.

## Visual quality target

The finished exterior must be visually convincing across principal viewpoints.
Centimetre accuracy, survey-grade reconstruction and exact photogrammetric camera
solutions are not required. Prioritise silhouette, proportions, characteristic
architecture, roof forms, facade rhythm and credible materials. Keep metre-scale
coherence and source/assumption traceability. Visually adequate approximations are
allowed when documented; do not invent measurements or metadata.

Use `docs/goals.md` for the three long work packages, completion criteria and
continuation checkpoints. Execute related sub-issues within their parent Goal;
an intermediate script, render or report alone does not complete a modeling Goal.

## Experimental isolation — mandatory

Work only from evidence and files in this repository plus the original public sources referenced here.

Do **not** use the sibling repository `KreutzM/E-Kirche` as a source of reconstruction answers. In particular, do not copy or inspect its:
- generated geometry;
- inferred dimensions;
- camera solutions;
- iteration reports;
- comparison renders;
- model-specific Blender scripts;
- later assumptions.

If an external source is required, record it explicitly and ensure it is freely accessible and licence-compatible.

## Required reading before modeling

Read, in order:

1. `EXPERIMENT.md`
2. `PROJECT.md`
3. `data/dimensions.yaml`
4. `data/manifest.json`
5. `docs/evidence_policy.md`
6. `data/assumptions.yaml`
7. relevant reference images/contact sheets

## Coordinate system

- Blender units: metres.
- X = East.
- Y = North.
- Z = Up.
- Origin = centre of the crossing at nominal floor level.
- Do not silently change this convention.

## Evidence precedence

When evidence conflicts:

1. verified/documented dimensions in `data/dimensions.yaml`;
2. multiple mutually consistent modern photographs;
3. historical architectural plans and sections;
4. historical photographs;
5. geometric inference.

Never present inferred geometry as measured geometry.

Every inferred dimension must be recorded in `data/assumptions.yaml` with:
- value and unit;
- reason;
- confidence: high / medium / low;
- supporting evidence IDs;
- iteration identifier.

## Modeling order

Work coarse-to-fine:

1. footprint;
2. nave / transept / triconch massing;
3. westwork and towers;
4. roofs;
5. buttresses;
6. primary openings;
7. tracery;
8. ornament.

Do not start decorative modeling until the massing passes dimensional and silhouette validation.

## Reproducibility

- Prefer Blender Python for repeated or procedural geometry.
- Keep repeated architectural elements parametric where practical.
- Treat the `.blend` file as a working artifact; scripts + parameters + evidence are the reproducible source.
- Never destructively edit files under `references/`.
- Never invent image metadata.
- Do not modify evidence to make it agree with the model.
- Keep model-specific logic in new scripts rather than hiding it in the Blender UI state.

## Blender collections

Use:
- MASSING
- TOWERS
- ROOFS
- BUTTRESSES
- OPENINGS
- TRACERY
- DETAIL
- CAMERAS
- REFERENCE

## Validation loop

After every material geometry change:

1. run `python scripts/validate_dataset.py`;
2. generate/update relevant validation renders;
3. compare silhouette, perspective structure and architectural landmarks;
4. record unresolved discrepancies;
5. update `data/assumptions.yaml` for new inferred dimensions;
6. keep uncertainty explicit.

Do not hide a mismatch by changing a validation camera without documenting the reason.

## Definition of done for an iteration

An iteration is complete only when:
- scripts execute without error;
- all new dimensions are either sourced or explicitly assumed;
- assumptions are current;
- changed geometry has been compared with relevant evidence;
- unresolved uncertainty is documented;
- no result from the earlier `E-Kirche` reconstruction was used as ground truth.
