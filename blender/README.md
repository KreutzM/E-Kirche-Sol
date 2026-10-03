# Blender workspace

Recommended scene: `blender/scene/elisabethkirche.blend`

G3-01 contains the final exterior, procedural materials, twelve retained validation
cameras and two separately documented presentation cameras. Use `git lfs pull`
after checkout. `python scripts/build_massing.py --final` regenerates the entire
delivery from factory settings, including GLB, renders and independent checks.
Parameters are `data/assumptions.yaml`, documented dimensions and `validation/cameras.json`.
The massing generator calls `scripts/blender/30_exterior_architecture.py` for Goal 2.
Do not run `00_scene_setup.py` on this working artifact unless resetting intentionally.
See `validation/reports/SOL-01.md` for review and simplifications. A saved-scene check
is `scripts/blender/96_verify_saved_exterior.py` (run in Blender on the `.blend`).

Large Blender files are prepared for Git LFS. The reproducible source of geometry remains Blender Python, documented dimensions and explicit assumptions. Avoid making the .blend file the only place where a geometric decision exists.
