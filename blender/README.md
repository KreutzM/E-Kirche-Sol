# Blender workspace

Recommended scene: `blender/scene/elisabethkirche.blend`

G1-04 contains the complete coarse exterior and twelve validation cameras.
Use `git lfs pull` after checkout. `python scripts/build_massing.py --render`
rebuilds from factory settings. Parameters are `data/assumptions.yaml`, documented
dimensions and `validation/cameras.json`; generator: `scripts/blender/20_goal1_massing.py`.
Do not run `00_scene_setup.py` on this working artifact unless resetting intentionally.
See `validation/reports/goal-1.md` for the massing gate and known simplifications.

Large Blender files are prepared for Git LFS. The reproducible source of geometry remains Blender Python, documented dimensions and explicit assumptions. Avoid making the .blend file the only place where a geometric decision exists.
