# Goal 2 — developed exterior architecture and materials

Issue #9. Review: 2026-10-02, **G2-04**. The architectural development gate is
accepted at level 3 for the supported principal views: the building is convincing
at normal whole-building viewing distance. This is a visual judgment under the
repository rubric, not a survey, pixel match or claim of exact sculptural fidelity.
Final delivery/export and a separate last quality pass remain Goal 3 (#8).

## Reproduce and inspect

```text
python scripts/validate_dataset.py
python scripts/build_massing.py --architecture --render
python scripts/make_massing_review.py --goal 2
python -m unittest discover -s tests -v
```

Blender 5.2.1 LTS was used. `--blender` or the `BLENDER` environment variable can
select an installation. Dependencies are in `requirements.txt`; the committed
cameras do not require the optional SciPy calibration dependencies.
The build starts from factory settings, reconstructs the accepted coarse masses,
then calls [30_exterior_architecture.py](../../scripts/blender/30_exterior_architecture.py)
to add architecture/materials before saving the
[working scene](../../blender/scene/elisabethkirche.blend). Git LFS distributes it.
Omitting `--architecture` rebuilds the older coarse stage and replaces the working scene.

Twelve neutral PNGs are generated in ignored `validation/renders/G2-04/`.
[Eleven attributed comparisons and two model diagnostics](../review/G2-04/README.md)
are retained in Git. Sources are resized without cropping or warping. Review
generation needs the original reference downloads; the model/material build itself
needs no photographs, external textures or network access.

Saved-scene verification:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background blender/scene/elisabethkirche.blend --python-exit-code 1 --python scripts/blender/96_verify_saved_exterior.py
```

## Architectural work and evidence

The [Goal-1 scale and source audit](goal-1.md) remains the basis. All six documented
dimension anchors and X east/Y north/Z up/metre/crossing-origin conventions are
preserved. Tower mesh height remains 80 m. The hall/transept/length scale proxies
remain 21.55, 39.17 and 55.59 m; these are rough interior cross-checks on exterior
volumes, not modeled interior dimensions or independent measurements.

- Nave and conches: two rows of pointed openings, paired lancets/rosettes,
  glazing, iron crossbars, profiled surrounds, sills, continuous cornices,
  stepped buttresses/weatherings and projecting drain silhouettes. Evidence:
  M04/M05/M06/M07/M18/M19 and P01/P02.
- Towers: lower windows, long belfry recesses, upper octagonal openings and stone
  gables, shoulder galleries/open parapets, corner support ledges and stone helms.
  M09/M10/M11 and P07 support the stage hierarchy.
- Westwork: a four-light central tracery window, deep nested portal archivolts,
  red double doors, central pier, abstract low-relief tympanum/figure, clock glazing,
  open dial/hands, gallery, small blind gables, pinnacles and crockets.
  Modern M10/M11/M12/M13/M14 supersede a literal copy of historical P03/P07.
- Sacristy: complete two-stage openings with paired lancets/quatrefoils, stepped
  supports, plinth, cornices, roof vent and drain heads. M15/M16/M17.
- Roofs: nave/side-roof/conch topology retained; western main roof terminates
  behind the towers with a low bridge roof. Rider foot is embedded into roof slopes,
  with open lantern cornices and terminal. Roof ridges/hips have metal seams;
  small vents and conch crosses are present. The reentrant stair has a coherent
  slate cap and small light slits. M01/M05/M17/M18 with P01/P02 cross-checks.

There are **117 blind exterior opening recesses**, not painted black wall patches.
They do not make an interior church model. Repeated facade modules are parametric;
each generated object records assumption/evidence provenance. The assumptions
file now contains **214 entries: 174 architectural and 40 camera scalars**.
Goal 2 added 123 architectural entries. Most detail dimensions are low-confidence
visual estimates, including the 0.42 m niche depth. No inferred number is promoted
to a measured value.

The original 32 reference hashes were rechecked and remain unchanged. No new
external source, texture, image metadata or result from the excluded sibling repo
was used. Attribution/share-alike terms are retained with redistributed composites.
No human modeling, sculpting or camera editing was needed.

## Materials

Procedural sandstone uses face-projected UVs in metres, staggered ashlar courses,
subtle joints/surface bump and broad world-space mottling. The 0.85 m block width,
0.34 m course height and 0.012 m joints are explicitly approximate visual scales.
Dressed mouldings have a quieter finish. Slate uses staggered 0.28×0.18 m exposed
units and fine seams/bump. Stone helms use sandstone, not slate. Glazing is a
blue-grey reflective exterior proxy with a fine lead network and real crossbars;
belfries remain dark. Iron, weathered lead/copper and red painted doors have
separate materials. These choices reproduce material character, not the exact
location of every weather stain, lead polygon or restored stone block.

## Iteration corrections and camera continuity

G2-01 established the whole architectural pass. G2-02 corrected an obstructed
clock niche, the portal-crossing plinth, weathering-cap overlaps and the overly
large rose on the four-light west window. G2-03 developed clock crest/portal detail,
completed the stair roof, embedded rider/vent bases and corrected the main roof's
west termination. G2-04 separated annex arch heads from the horizontal division,
wrapped ledges around tower corner supports, unioned their crossed coplanar pieces,
opened plinth gaps at side doors and softened excessive ashlar colour contrast.
Portal surrounds were clamped to nominal floor level after a bounds check found
their lower edges extending below it.

All **twelve camera configurations are unchanged** from Goal 1; no photographic
camera was refitted to improve apparent agreement. Neutral lighting is also
retained; sampling increased from 32 to 48 with denoising. Photo-fit limitations,
manual correspondences and camera history remain as recorded in goal-1.md.
Especially S/N/SW have imperfect perspective/framing; VAL_S_M04 is a supplementary
uncalibrated diagnostic. Elevated/annex views are inspection views, not solved
source-photo poses. Photograph light/vegetation/street context is not reproduced.

## Per-view visual acceptance

All twelve final renders and eleven source/render composites were actually inspected.
Scores below apply at normal whole-building viewing scale. Simplified fine carvings
and uncertain hidden details are evaluated as such, not claimed as exact copies.

| View / evidence | Silhouette & proportions | Roof form | Facade rhythm | Distinctive architecture | Materials | Review and explicit limits |
| --- | --- | --- | --- | --- | --- | --- |
| W / M10, M11; M12–M14 details | 3 | 3 | 3 | 3 | 3 | Complete paired-tower front, staged ledges, portal, clock crest and four-light window; carving/tracery patterns simplified, patina not photograph-matched. |
| SW / M09 | 3 | 3 | 3 | 3 | 3 | Strong tower taper and projecting stage hierarchy; close upward view reveals economical archivolt/ledge profiles. Fine crocket/terminal shapes and exact pose remain approximate. |
| S / M05, M04; M18/M19 | 3 | 3 | 3 | 3 | 3 | Two tiers, lancet/rose heads, stepped supports and roof rider read coherently; source partial oblique and different foreshortening remain visible. Exact spout creatures and lead layout simplified. |
| SE / M02, M03, M19 | 3 | 3 | 3 | 3 | 3 | Complete recognizable conch/tower composition and roof hierarchy; coherent cap openings and annex. Small roof vents and geometric cap regularization remain visual estimates. |
| N / M06, M07 | 3 | 3 | 3 | 3 | 3 | Complete northern bay rhythm, buttresses and tower stages; far-tower overlap differs with approximate pose. Surface aging is intentionally generic. |
| Elevated NNE / M01 | 3 | 3 | 3 | 3 | 3 | Continuous complete roof network and developed facade perimeter; M01 is only 600 px and camera differs, so hidden-valley construction and exact roof-unit pitch are not proven. |
| NE / M15–M17 | 3 | 3 | 3 | 3 | 3 | Annex is developed with two window stages, differentiated quatrefoil heads, supports and lower roof. Exact foliation and roof vent profile are simplified. |

Plan P01/P08 and orthographic P02/P07 checks preserve the accepted structure and
height hierarchy; buttress projections are now visible in plan. P02 truncates the
towers and depicts a historical roof rider. The east orthographic is fully developed
and was inspected with historical H01 as a coverage aid. H01 cannot establish exact
present-day details; modern SE views constrain the east cap obliquely. No modern
direct east photograph is claimed. There is no visibly blank major facade or
unfinished main roof in the supported views.

Remaining economical simplifications: regularized sandstone course lengths and
cap facets, generic glazing lead pattern, abstract portal sculpture/foliage,
reduced crockets/finials/spout beasts and a low-confidence reentrant stair light
pattern. These are deliberate visual approximations, not missing whole facade
work. Tiny physical junctions should receive the final neutral-light check in #8.
No centimetre-accuracy or close-up sculptural reproduction is claimed.

## Verification and next Goal

[Build checks](goal-2-build.json), [opening inventory](goal-2-architecture.json) and
[saved-scene verification](goal-2-reopen.json) provide runtime evidence. A fresh
factory-startup build and all twelve renders complete without script errors.
Dataset validation, nine pipeline tests, compilation and whitespace checks pass.
The saved scene independently reopens with 1,460 closed individual meshes and
1,539 capped profile curves; all architectural collections are populated, mesh
materials/UVs are present, provenance is nonempty and bounds span z=0..80 m.
A ray into a regular nave opening confirms actual 0.42 m wall recess depth and
separate glazing in front of its rear stone surface. Camera position/lens/view
directions match the retained configuration. No temporary cutter remains.

The meshes overlap intentionally as exterior architectural components; the model
is not a global watertight union or a usable interior. Procedural Blender materials
will require export handling for GLB; this is explicitly part of #8, together with
final neutral review, presentation renders, reimport validation and SOL-01 report.
The current Goal-2 scene and comparison evidence are delivered through Git/Git LFS.
