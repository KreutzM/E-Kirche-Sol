# Reconstruction progress

## WEB-01 browser presentation — 2026-10-03

The independent SOL-01 model now has a reproducible Three.js/TypeScript web
presentation under [web/](../web/README.md). Lossless Meshopt reduces the GLB
from 20.2 MB to 11.2 MB while retaining decoded geometry, textures and transforms.
Web cameras/light are separate from the frozen reconstruction and its validation.
Desktop and emulated mobile WebGL acceptance is documented in
[WEB-01](../validation/reports/WEB-01.md). The [live player](https://kreutzm.github.io/E-Kirche-Sol/)
is published via Pages Actions. Eight checks pass on the public site and in Linux
CI; all ten published files match the build artifact, including original downloads.
Real RTX 3060 measurements show approximately 60 fps. Mobile touch/layout is
emulated, with that performance limitation recorded. All SOL-01 artifacts remain
unchanged. No delivery blocker remains.

## SOL-01 final delivery — 2026-10-03, G3-01

The three reconstruction packages are implemented: Goal 1 #2 with #3–#7,
Goal 2 #9 and final Goal 3 #8. Sources/assumptions and original geometry remain
independent of the excluded sibling reconstruction. No external blocker or human
modeling/export assistance was required.

Final report: [SOL-01.md](../validation/reports/SOL-01.md).
Artifacts: [Blender](../blender/scene/elisabethkirche.blend),
[GLB](../blender/exports/elisabethkirche_SOL-01.glb),
[full-resolution gallery](../validation/delivery/SOL-01/README.md),
[attributed comparisons](../validation/review/G3-01/README.md).
The generated assets have a documented free licence and retained source attribution.

- Full factory-startup `python scripts/build_massing.py --final` exits 0, including
  fourteen neutral/presentation renders, portable texture baking/export,
  independent saved-scene checks and fresh GLB import/two review renders.
- Original G2-04 architecture retained after the final multi-view review. All
  twelve validation configurations, including roll, are unchanged. Two presentation
  cameras are separately documented; neutral lighting is retained.
- Saved scene: 1,460 closed individual meshes, 1,539 capped profile curves,
  nine required collections; bounds z=0..80 m. Real window niche sample remains
  0.42 m with separate glazing in front of its rear stone surface.
- Portable GLB: 20,201,684 bytes, 19 collection/material batches, 497,144 triangles,
  nine materials and six embedded 1024² images. Bounds/axes/metres match on reimport.
  All 2,999 components are accounted for by batch metadata.
- Six source anchors, 214 assumptions (174 architecture, 40 camera scalars);
  no new building dimension in this final delivery stage. All 32 reference hashes
  unchanged. Dataset validation, nine pipeline tests and compilation pass.
- Sixteen full-resolution PNGs and eleven attributed comparisons inspected;
  visual level 3 across supported main/roof views at normal whole-building distance.
  Runtime checks and artifact checksums are in `validation/reports/SOL-01-*.json`.

## Reproduce and freeze

```text
git lfs pull
python scripts/build_massing.py --final
```

The build needs Blender and `requirements.txt`, but no original images or network
after dependencies are installed. Optional attributed composites need downloaded
references: `python scripts/make_massing_review.py --goal 3`.

The commit introducing `validation/reports/SOL-01.md` freezes the independently
generated result; retrieve it with
`git log --diff-filter=A -1 --format=%H -- validation/reports/SOL-01.md`.
Issue #8 records the full commit identifier and publication verification after
push. Blender/GLB/final PNGs are delivered through Git LFS; review JPEGs/report/code
remain ordinary Git. Opening a pointer file without `git lfs pull` is insufficient.

## Remaining documented limits

Generic stone aging/glazing lead network, abstract portal sculpture/foliage,
reduced crockets/finials/drain creatures, regularized cap facets and low-confidence
stair lights remain visual approximations. GLB patina repeats baked swatches rather
than preserving a continuous world-space shader. Photo poses are approximate;
there is no direct modern east reference, and M01's original is small. Overlapping
exterior components do not provide a globally watertight model or usable interior.
No centimetre accuracy or human final visual sign-off is claimed.

There is no remaining reconstruction package in this experiment's three-Goal plan.
Any comparison with the excluded sibling requires a separate user instruction
after the independent freeze.

Historical milestones: Goal 1 `fdc46f5`, Goal 2 `4cf68cd`; their reports and comparisons
remain retained. Omitting `--final` and using the older coarse/build flags replaces
the working scene with that earlier stage.
