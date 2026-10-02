# Reconstruction progress

## Goal 2 delivered — 2026-10-02, G2-04

Issue #9 reaches the architectural development gate at visual level 3 under the
normal whole-building viewing rubric. All principal neutral comparisons and the
elevated roof/plan/elevation checks were generated and actually inspected.
Report: `validation/reports/goal-2.md`. Review images and attribution:
`validation/review/G2-04/README.md`. Working scene:
`blender/scene/elisabethkirche.blend` (Git LFS).

- Whole exterior developed: two-tier recessed glazing/tracery, buttresses/cornices,
  tower belfries/gables/galleries, west portal and clock crest, annex and roof details.
- Procedural metre-scale sandstone/slate, exterior glass, metal and red timber materials.
- 214 explicit assumptions: 174 architecture, 40 camera parameters; six source anchors unchanged.
- 117 blind opening recesses; saved-scene check confirms 0.42 m sample niche depth,
  separate glazing and all twelve retained camera configurations.
- Fresh Blender 5.2.1 LTS build, twelve renders, saved-scene verification, dataset
  validation, nine pipeline tests, compilation and whitespace checks pass.
- 1,460 closed individual meshes, 1,539 capped profile curves; z=0..80 m.
- 32 reference hashes unchanged; no sibling reconstruction, external texture or
  invented photo metadata used. No external blocker.

The delivery commit introduces `goal-2.md`; retrieve its identifier with
`git log -1 --format=%H -- validation/reports/goal-2.md` after checkout.

## Reproduce

```text
git lfs pull
python scripts/validate_dataset.py
python scripts/build_massing.py --architecture --render
python scripts/make_massing_review.py --goal 2
python -m unittest discover -s tests -v
```

Review generation needs the original downloaded references. Omitting
`--architecture` replaces the scene with the older coarse stage.

## Next: Goal 3 / #8

[Issue #8](https://github.com/KreutzM/E-Kirche-Sol/issues/8) remains open: final neutral
quality pass, usable GLB export with material handling, export reimport checks,
five principal neutral and two presentation renders, reproducible delivery and SOL-01.
No Goal-3 work has started. Check tiny physical junctions and normal-distance
appearance without discarding the retained comparison cameras.

Explicit approximations: generic stone aging/lead network, abstract portal figure
and foliage, reduced crockets/finials/spout creatures, regularized cap facets and
low-confidence stair lights. Photo poses remain approximate; no modern direct east
photo exists, and M01 is small. These do not imply exact source agreement. See the
Goal-2 report for per-view limits and acceptance reasoning.

Goal 1 (#2, #3–#7) was delivered in `fdc46f5`; its report/comparisons remain retained.
The working scene is now Goal 2. The entire final-delivery contract awaits #8.
