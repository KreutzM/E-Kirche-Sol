# Goal 1 — independent complete coarse exterior

Review date: 2026-10-02. Iteration: **G1-04**. Scope: #2 and #3–#7.
The coarse massing gate is accepted at rubric level 2. This is a recognizable,
coherent exterior base for Goal 2, not the finished visually convincing model.
No sibling reconstruction was inspected or used. Human input was limited to the
repository brief and the clarification that visual quality matters more than
centimetre accuracy; no manual Blender modeling or camera solution was supplied.

## Delivered and reproducible

- [Working scene](../../blender/scene/elisabethkirche.blend), distributed via Git LFS.
- [Generator](../../scripts/blender/20_goal1_massing.py), launched by
  [build_massing.py](../../scripts/build_massing.py).
- [Eleven attributed evidence/render comparisons](../review/G1-04/README.md).
- [Build checks](goal-1-build.json), [saved-scene checks](goal-1-reopen.json),
  [camera fit residuals](goal-1-camera-fit.json).
- [Assumptions](../../data/assumptions.yaml), [camera configuration](../cameras.json),
  [manual landmarks](../landmarks.yaml), [camera history](../camera_history.json).

From the repository root with dependencies and Blender installed:

```text
python scripts/validate_dataset.py
python scripts/build_massing.py --render
python scripts/make_massing_review.py
python -m unittest discover -s tests -v
```

The build starts from factory settings, writes the scene and generates twelve
neutral PNGs under ignored `validation/renders/G1-04/`. Review JPEGs are tracked;
they retain full source framing. Original references are acquired independently:
`python scripts/fetch_assets.py --max-width 2500` followed by
`python scripts/make_contact_sheets.py`. No network access is needed for the model
build after dependencies are installed. Review generation needs those references.
Optional camera refitting uses `requirements-calibration.txt`; it is not needed
to reproduce the committed scene. Reopening verification:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background blender/scene/elisabethkirche.blend --python-exit-code 1 --python scripts/blender/95_verify_saved_massing.py
```

## Evidence audit

All **32/32** manifest references were checked through live Commons imageinfo,
licence-gated downloaded, SHA-256 recorded and Pillow-readability verified.
There were no failed downloads. Five contact sheets (overview, west, south, north,
plans) and relevant individual photographs/plans were actually inspected.
[reference_audit.json](../../sources/reference_audit.json) retains all source URLs,
artists, credits, dates, licence links, actual image sizes and local hashes.
Public source metadata is also retained in
[commons_download_metadata.jsonl](../../sources/commons_download_metadata.jsonl).
Distributed comparison images carry per-image attribution and share-alike terms.
Original files under `references/` were never modified.

M04/M05/M06/M07/M09 are partial close obliques, not complete unobscured elevations.
H02/H03 are distant city panoramas with limited church measurement utility.
M01's original is only 600×600, limiting fine roof inference. M08 remains excluded
from pinhole fitting per its manifest classification; no projection metadata was
invented. No additional external image source was necessary for this coarse stage.
[Coverage](../../data/coverage.yaml) records the direct modern east-view gap and
limited roof-valley visibility. Oblique modern views plus historical plans suffice
for coherent massing; they do not prove hidden fine details.

The two original dimension pages were opened and verified during this Goal:
[official church description](https://www.elisabethkirche.de/kirchenraum/sehenswuerdiges/allgemeines)
and [Dehio building record](https://de.dehio.org/bauwerk/marburg-elisabethkirche).
The six existing source anchors retain their interior/exterior scope unchanged.

## Scale, orientation and inferred geometry

Metres; X east, Y north, Z up; crossing centre at nominal floor level is the origin.
P01 is interpreted with east at the top and north to the left. The coarse outline
was visually scaled against the documented interior hall width, not inferred from
a pier-centre span as if it were a clear interior measurement. The illustrative
hand reading used a 1312×1877 display of P01, approximate crossing centre (606.5,665)
and hall inner walls at x≈400 and 815: 21.55/415≈0.05193 m/display pixel. This is an
approximate reading, not a survey or exact tracing. P08 and modern views cross-check it.

| Source anchor | Meaning | Coarse check | Interpretation |
| --- | --- | --- | --- |
| ~80 m tower height | Exterior, official | Highest mesh vertex 80 m | Approximate source height, not centimetre precision |
| 21.55 m hall width | Interior | 23.95 exterior minus 2×1.20 effective wall zone = 21.55 m | Constructed scale proxy; not independent validation |
| 39 m transept | Interior, Dehio | 39.17 m after assumed cap wall zones | +0.44%; no modeled interior surface |
| 56 m length without west hall | Interior, Dehio | 55.59 m after assumed eastern cap offset | −0.74%; not total exterior length |
| 10 m crossing square | Clear interior | 10.9 m inferred structural pitch | Distinct quantities; no equality claimed |
| 20.20 m vault height | Interior | Exterior eave assumed 22 m, ridge 32 m | Plausible vertical hierarchy, vault not modeled |

There are 51 architectural assumptions and 40 photo-camera scalar assumptions,
each with numeric value/unit, reason, confidence, evidence IDs and iteration.
The camera target coordinates only encode viewing direction; they are not building
measurements. Inspection-camera framing, lights and render settings are presentation
parameters in the camera configuration/generator.

The generated model contains 60 architectural meshes: seven principal masses,
25 tower pieces and 28 roof pieces. Main masses include the hall, three polygonal
conches, west connecting volume, NE sacristy and north reentrant stair. Roofs include
the longitudinal nave roof, three conch gable/hip roofs, five transverse units on
each hall side, annex roof and modern open-lantern crossing rider. Towers have
coarse staged corner supports, upper octagonal stages, corner turrets and stone helms.
All prescribed collections exist; detail collections are intentionally empty.
Individual meshes are closed. Intersecting coarse volumes are not a single
watertight union and do not provide usable interior rooms.

## Camera method and iteration history

W/SW/S/SE/N poses were independently fitted to manually selected silhouette/roof
landmarks. A 36 mm horizontal sensor convention, sector bounds and weak eye-height
priors keep the process repeatable. Lens values are approximate; no EXIF-derived
physical calibration is claimed. RMS residuals are roughly 0.012–0.037 in normalized
image-coordinate units and describe these chosen correspondences only. They are
not independent geometric accuracy or an acceptance threshold.

G1-01 established the full scene. G1-02 refined photo framing and corrected duplicated
west wall geometry. G1-03 extended side roofs under the central roof and improved
roof/plan inspection framing. G1-04 unioned tower shaft/support meshes and separated
coplanar west roof/wall faces by a numerical 1 mm offset to remove render artifacts;
that offset is numerical construction tolerance, not a measured architectural feature.

A mistaken M02 landmark association was corrected: its foreground right cap is
east, not south. The SE camera was refitted against the corrected correspondence,
without moving architecture to match the mistake. An unrestricted S fit produced
an implausible ~14° lean; roll was then constrained to ±2.865° because M05's rider
is nearly upright. The larger residual is retained. All pose changes and prior
configurations are documented in camera_history.json. Cameras were not changed to
hide a known geometry defect. Elevated/annex/orthographic views are clearly labeled
diagnostics, not solved photographic matches. VAL_S_M04 is especially poorly matched
and is retained only as a supplementary framing check.

## Visual review and unresolved discrepancies

Scores use the repository's rubric: 2 = coherent/recognizable with visible refinement
needed. Judgments are visual, not measured accuracy. All eleven tracked comparisons
and the east orthographic render were inspected. Historical drawings supplement
modern evidence but do not determine present-day roof-rider detail.

| View / evidence | Silhouette | Proportions | Roof form | Finding and next refinement |
| --- | --- | --- | --- | --- |
| W / M10, M11 | 2 | 2 | 2 | Paired towers, staged shoulders and helms read correctly; upper-stage gables, gallery ledges and central facade crest are simplified. West connecting gable is too plain. |
| SW / M09 | 2 | 2 | 2 | Close upward tower ordering and taper are plausible; support profiles and ledges are blocky, base cropped in both frames. |
| S / M05, M04 | 2 | 2 | 2 | South conch, side-roof rhythm and modern rider recognizable; rider support junction/height and exact conch roof planes need refinement. Partial view and pose mismatch remain. |
| SE / M02, M03, M19 | 2 | 2 | 2 | Strong overall check: tower pair, east/south caps, saddle connection and NE annex present. Roof valleys/overhangs and tower upper proportions remain approximate. |
| N / M06, M07 | 2 | 2 | 2 | Two towers and northern roof sequence coherent; near tower appears broader, farther spire more occluded than photograph. Keep this discrepancy visible during Goal 2. |
| Elevated NNE / M01 | 2 | 2 | 2 | Overall roof topology recognizable; different camera/framing, exact transverse-unit pitch and hidden valleys uncertain. No aerial camera match claimed. |
| NE annex / M16, M17 | 2 | 2 | 2 | Correct reentrant annex location and lower roof hierarchy; roof profile, plinth and two-stage facade require detail work. Diagnostic pose differs. |
| Plan / P01, P08 | 2 | 2 | 2 | Correct triconch orientation, hall proportions and NE annex; caps regularized, masonry offsets/coarse support depth not exactly traced. Roof plan differs from ground plan by overhang. |
| S/W/E orthographic / P02, P06, P07, H01 | 2 | 2 | 2 | Height hierarchy and primary volumes coherent. P02 truncates towers; historical rider differs. Modern direct east detail still unsupported. |

Facade rhythm/openings, distinctive fine architecture and finished materials are
not accepted at this stage: most surfaces are blank, and neutral clay colours are
only for massing inspection. They are the explicit work of #9, followed by final
quality/export/delivery in #8. The whole project is not yet visually finished.

Highest-impact next work: add two-level opening rhythm and characteristic buttresses,
refine tower galleries/gables and roof junctions, then stone/slate/glazing materials.
Retain the current views so these refinements can be checked without resetting
the comparison basis. Roof-unit count, rider height, regularized cap shape and
hidden east details remain marked assumptions rather than measurements.

## Verification

Dataset validation, nine offline pipeline tests, Python compilation and whitespace
checks pass. A factory-startup Blender 5.2.1 LTS build and all twelve renders completed
without script errors. A separate reopening check verifies units, coordinate/origin
metadata, required collections, twelve cameras, two tower shafts, 60 closed individual
architectural meshes with provenance, and an actual maximum vertex height of 80 m.
These checks establish reproducibility and coarse integrity, not final visual polish.
