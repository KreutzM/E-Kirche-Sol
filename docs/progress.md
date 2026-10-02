# Reconstruction progress

## Goal 1 delivered — 2026-10-02, G1-04

Goal 1 (#2 including #3–#7) reaches the coarse massing gate at visual level 2.
The complete coarse exterior includes hall, triconch, westwork, both towers,
primary roofs, sacristy and reentrant stair. Details/materials remain Goal 2 work.
Working scene: `blender/scene/elisabethkirche.blend` (LFS). Delivery commit: the
commit introducing this checkpoint; find it with
`git log -1 --format=%H -- validation/reports/goal-1.md` after checkout.

- 32/32 live licence-checked references downloaded; hashes/readability verified.
- Five contact sheets and relevant individual evidence actually inspected.
- Six source anchors unchanged; 51 architectural plus 40 camera assumptions.
- Twelve renders and eleven attributed comparisons in `validation/review/G1-04/`.
- `validation/reports/goal-1.md` records per-view scores, scale proxies, camera
  limitations, corrections and remaining discrepancies.
- Dataset validation, nine pipeline tests, compilation, fresh build and saved-scene
  reopening verified. No external blocker or excluded-repository use.

## Reproduce and continue

```text
git lfs pull
python scripts/validate_dataset.py
python scripts/build_massing.py --render
python scripts/make_massing_review.py
python -m unittest discover -s tests -v
```

Review generation needs downloaded references. Blender 5.2.1 LTS was used.
Next: [Goal 2 / #9](https://github.com/KreutzM/E-Kirche-Sol/issues/9), characteristic
buttresses and two-level openings first, then tower galleries/gables, roof junctions
and stone/slate/glazing materials. Refine coarse masses as evidence warrants.
Keep comparison cameras and record changes. Residuals: approximate N tower overlap,
S perspective mismatch, simplified west gable/upper stages, rider junction/height,
side-roof pitch/count and hidden east details. No modern direct east photo; M01 is
small. Full findings are in the Goal-1 report.

Finally [Goal 3 / #8](https://github.com/KreutzM/E-Kirche-Sol/issues/8): final quality,
GLB export, presentation renders and SOL-01 delivery. Goals 2 and 3 have not started.
The finished-model visual target has not yet been reached.
