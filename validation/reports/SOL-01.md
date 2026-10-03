# SOL-01 — independent Elisabethkirche exterior delivery

Issue #8, final iteration **G3-01**, review date 2026-10-03.
Final clean build, saved-scene reopen, fresh GLB import and visual review passed.
Scope: present-day exterior in metres; visually convincing at normal whole-building
viewing distance. This is an independent GPT-6.1-Sol reconstruction from the
repository evidence, not a survey or centimetre-accurate photogrammetric result.

## Deliverables and reproduction

- [Editable Blender scene](../../blender/scene/elisabethkirche.blend), with individual
  procedural components, provenance, materials, collections and cameras.
- [Self-contained GLB](../../blender/exports/elisabethkirche_SOL-01.glb), with portable
  PBR materials and embedded colour/normal images; [export guide](../../blender/exports/README.md).
- [Full-resolution gallery](../delivery/SOL-01/README.md): twelve neutral validation
  views, two presentation views and two renders of the actually reimported GLB.
- [Eleven attributed photo/plan comparisons](../review/G3-01/README.md), including
  W/SW/S/SE/N, roof, annex, plan and elevations; two model-only diagnostics.
- [Artifact hashes and sizes](SOL-01-artifacts.json), [saved-scene checks](SOL-01-reopen.json),
  [fresh GLB import checks](SOL-01-glb-check.json), [build scale checks](SOL-01-build.json),
  [opening inventory](SOL-01-architecture.json), [export/material inventory](SOL-01-export.json),
  [render resolutions/purposes](SOL-01-renders.json).
- [Generated asset licence/source attribution](../delivery/SOL-01/LICENSE.md).

After installing `requirements.txt` and Blender, from the repository root:

```text
git lfs pull
python scripts/build_massing.py --final
```

The one build command starts Blender from factory settings, reconstructs the model
from canonical dimensions/assumptions, creates all cameras and procedural materials,
renders all fourteen delivery views, bakes portable materials and exports GLB.
It then starts separate Blender processes to reopen/check the saved scene and
import/check/render the GLB. Every invocation uses `--python-exit-code 1` and the
launcher propagates failure. The tested installation is Blender 5.2.1 LTS with
Python 3.11.9 for the launcher. Select Blender with `--blender` or `BLENDER` if needed.
No reference photos, external textures, SciPy or network are needed for this build.
Images may differ slightly across Blender/platform/render versions; semantic
reproducibility does not imply byte-identical `.blend`/PNG output.

Optional source composites require original Commons downloads:

```text
python scripts/fetch_assets.py --max-width 2500
python scripts/make_massing_review.py --goal 3
python scripts/validate_dataset.py
python -m unittest discover -s tests -v
```

The gallery PNGs, `.blend` and GLB are committed via Git LFS. The attributed JPEG
comparisons and reports remain ordinary Git files. Ignored intermediate bake PNGs
are not required by the embedded GLB. Use `git lfs pull` to retrieve actual binaries,
rather than opening LFS pointer text. All links above are repository-relative.

## Evidence, dimensions and confidence

[EXPERIMENT.md](../../EXPERIMENT.md) and [AGENTS.md](../../AGENTS.md) define isolation,
axes, source precedence and the exterior scope. X east, Y north, Z up, crossing
centre at nominal floor level; Blender unit scale is one metre. No sibling model,
script, camera, assumption, report or rendered result was inspected.

The initial 32 sources were independently acquired and audited in Goal 1.
[reference_audit.json](../../sources/reference_audit.json) preserves authors,
credits, licences, original URLs, image sizes and hashes. Original files remain
untouched. Modern photographs constrain present-day details; historical plans
and H01 aid structural/occluded geometry with condition caveats. No new external
reference or photographic metadata was introduced in Goal 3.

The six anchors in [dimensions.yaml](../../data/dimensions.yaml) retain their scope:

| Anchor | Original source | Final interpretation/check |
| --- | --- | --- |
| Approx. 80 m towers | [Official church description](https://www.elisabethkirche.de/kirchenraum/sehenswuerdiges/allgemeines) | Actual highest tower vertices 80 m; approximate source, no centimetre precision |
| 21.55 m hall width | Official church description | Interior. Assumed exterior 23.95 m minus two 1.20 m effective wall zones reproduces it by construction |
| 10 m crossing square | Official church description | Clear interior reference; inferred structural pitch 10.9 m is a different quantity |
| 20.20 m vault height | Official church description | Interior vault not modeled; exterior eave 22 m and ridge 32 m give plausible hierarchy |
| 39 m transept | [Dehio](https://de.dehio.org/bauwerk/marburg-elisabethkirche) | Interior proxy 39.17 m after assumed cap offsets; approximately +0.44%, not an independent measurement |
| 56 m length without west hall | Dehio | Interior proxy 55.59 m, approximately −0.74%; not overall exterior length |

All inference remains in [assumptions.yaml](../../data/assumptions.yaml): **214
entries**, including 174 architectural parameters (1 high, 32 medium, 141 low)
and 40 low-confidence camera scalar assumptions. Every entry has a numeric value,
unit, reason, supporting manifest IDs and iteration. Examples: outer hall width
23.95 m (medium), cap centre 15.2 m (medium), wall eave 22 m (medium), blind opening
depth 0.42 m (low), sandstone course 0.34 m (low), exposed slate course 0.18 m (low).
These are visual/structural estimates, not measured masonry or camera calibration.
G3-01 introduces no architectural dimension: the final review retained G2-04
geometry and assumptions. Bake patch sizes and presentation poses are rendering/
export settings derived from existing material scales, not new building evidence.

## Final review and camera continuity

The final pass checks every side, plan/elevations and the roof network under neutral
lighting. The twelve validation configurations in [cameras.json](../cameras.json)
are unchanged; positions/lenses/directions are checked after reopening. Source
fitting, landmarks and history remain in the Goal-1 records. Photographs are not
warped or cropped to force agreement. Partial source views and approximate camera
poses are acknowledged rather than converted into metric confidence.

Two separately named `PRES_SE`/`PRES_NW` cameras are documented in
[presentation_cameras.json](../presentation_cameras.json). They frame the entire
building obliquely and are not photograph solutions. Both use the same neutral
sun/world/AgX setup as validation. Final sampling is 64 with denoising; the reimport
checks use 48. Delivery images have a long edge of at least 1800 px; presentation
images are 2000×1800. No lighting change is used to conceal geometry discrepancies.

Visual scores follow [docs/goals.md](../../docs/goals.md): 3 means convincing at
normal viewing distance with minor or explicitly uncertain deviations. Scores
are documented agent judgment, not an external review or measured accuracy.

| View / evidence | Silhouette / proportions | Roofs | Facade rhythm | Distinctive architecture | Materials | Findings and retained deviations |
| --- | --- | --- | --- | --- | --- | --- |
| W / M10–M14 | 3 | 3 | 3 | 3 | 3 | Paired stages/stone helms, projecting ledges, gallery, central clock crest, deep red-door portal and four-light window read clearly. Portal figure/foliage, gable leaves and fine tracery are economical approximations; stone aging is generic. |
| SW / M09 | 3 | 3 | 3 | 3 | 3 | Tower taper, corner supports and belfry depth remain coherent in upward view. Thin profiles and terminal ornaments are simplified; exact photographed pose/foreshortening differs. |
| S / M05; M04, M18/M19 | 3 | 3 | 3 | 3 | 3 | Two-tier lancet/rose rhythm, cap supports, eave/weathering levels and open-lantern rider are continuous. Drain silhouettes lack exact animal sculpture; glazing lead pattern is approximate. M04 remains an additional uncalibrated partial view. |
| SE / M02/M03/M19 | 3 | 3 | 3 | 3 | 3 | Recognizable three-conch composition, tower/roof hierarchy and developed exterior. Cap polygon regularization, tiny vents and source light/street occlusion differ. |
| N / M06/M07 | 3 | 3 | 3 | 3 | 3 | Developed nave rhythm, support tiers and complete towers. Far-tower overlap depends on approximate pose; patina/restored-stone distribution is not copied pixel for pixel. |
| Elevated NNE / M01 | 3 | 3 | 3 | 3 | 3 | Main/cap/side roofs, attached annex and rider form a coherent network. M01 is only 600 px; hidden valley construction and fine roof-unit pitch remain uncertain. |
| NE annex / M15–M17 | 3 | 3 | 3 | 3 | 3 | Two window rows/quatrefoil heads, stepped supports, pyramidal roof and vent are developed. Exact foliation, weather staining and vent carving remain simplified. |

The south, west and east orthographics plus plan were checked for continuity,
floating primary parts, unintentional holes and inconsistent bay/material scale.
P01/P08 support layout; P02/P07 support height relationships with historical
condition caveats. East is a coherent modeled facade constrained obliquely by
modern SE photographs and historically by H01; no direct modern east-view match
is claimed. Roof rider/vents penetrate their supporting roofs as documented in
Goal 2. Intended component overlaps remain; no conspicuous detached primary part
or visibly unfinished major facade was found at the stated viewing scale.

## Portable materials and validation limits

The editable scene retains metre-projected procedural sandstone/slate and exterior
glazing. The GLB converts these to shared 1024² base-colour/tangent-normal swatches,
preserving their architectural UV scale and roughness/metallic factors. Stone
patches cover eight blocks by twelve courses; slate patches use the same count.
Continuous world-space patina becomes a repeating sampled patch. This causes
small appearance differences, explicitly accepted after reimport render review;
it is not an exact shader translation. Dressed stone, iron, flashings, red timber,
portal relief and dark belfries retain constant PBR colours. No photographic
texture or external image file is embedded.

Curves are converted to meshes only in an export copy; components are batched by
source collection/material. The editable file retains individual names and
parameter/evidence tags. GLB extras identify source collection and component
count. Ground/cameras/lights are excluded. glTF's Y-up conversion reverses correctly
on import; bounds and metre scale are checked against the reopened Blender scene.
Embedded images are inspected for actual presence, dimensions and packed data.
The SE and W export renders use exclusively reimported architecture/materials;
only stage/cameras are appended from the editable scene.

Meshes are closed individual components, not a globally watertight union. Interior
rooms, hidden construction and exact sculptural reproduction are outside scope.
Regularized stone block lengths/cap facets, generic leadwork, abstract portal
sculpture, reduced crockets/finials/drain beasts and low-confidence stair lights
remain deliberate approximations. Evidence gaps are recorded in
[coverage.yaml](../../data/coverage.yaml). These limits are relevant to close-up,
survey, restoration, fabrication or interior use; this delivery targets exterior
visualization at normal whole-building distance.

## Verification, independence and freeze

Runtime evidence is linked above. Dataset validation checks 32 reference records,
6 source anchors and 214 assumptions; all nine relevant pipeline tests pass.
The complete `python scripts/build_massing.py --final` command exited **0**.
The editable file reopened with **1,460 closed meshes and 1,539 capped curves**,
all nine required collections, twelve stable validation cameras (including roll)
and two checked presentation cameras. Actual bounds are X −47.39..23.33 m,
Y −23.33..23.33 m, Z 0..80 m. The imported **20,201,684-byte GLB** matches those
bounds, contains **19 batches, 497,144 triangles, 9 materials and 6 embedded
1024² images**, and preserves all 2,999 source components through its batch counts.
All **16 final PNGs and 11 attributed comparisons** were actually inspected;
32 original reference hashes remain unchanged. Artifact hashes are recorded for
the Blender file, GLB and every delivered full-resolution image.
The final command performs a clean full Blender build, saved-file reopen checks
and a fresh-process GLB import, validates collection content/geometry/materials,
matches actual bounds and produces separate export review renders. Each individual
editable mesh is checked for manifold edges; capped profile curves are checked
separately. Runtime checks do not certify exact photographic correspondence.
Visual acceptance additionally requires the actual rendered comparisons and
export images to be inspected, not merely successful script exit codes.

Original reference hashes are checked when the downloads are present. No human
Blender modeling, camera editing, sculpting, texture creation or export assistance
was required. Human intervention was limited to the initial repository/evidence
brief, the preference for convincing appearance over centimetre accuracy, and
instructions to execute the three Goals. No human final visual sign-off is claimed.

The independent freeze is the commit introducing this report and final artifact
set. Retrieve its immutable identifier with:

```text
git log --diff-filter=A -1 --format=%H -- validation/reports/SOL-01.md
```

The completed issue records the explicit full delivery commit ID after commit/push,
avoiding a self-referential hash inside the same commit. Freeze precedes any
separately authorized comparison with the excluded sibling experiment.
