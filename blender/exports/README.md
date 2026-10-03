# SOL-01 portable exterior

[Download the self-contained GLB](elisabethkirche_SOL-01.glb) with Git LFS:

```text
git lfs pull
python scripts/build_massing.py --final
```

The single build command regenerates the editable model, procedural materials,
all neutral/presentation renders, portable material swatches, GLB and fresh-process
reopen/import verification. Blender 5.2.1 LTS and `requirements.txt` were used;
select another installation with `--blender` or `BLENDER`.

The GLB includes the exterior only: seven architectural collection groups batched
by material, converted profile curves, base colours, roughness/metallic factors,
three base-colour and three tangent-normal images embedded in the binary. No
external textures, ground, lights or cameras are required. glTF uses Y up; the
exporter converts Blender (X east, Y north, Z up) to (X, Z, -Y) without changing
metre scale or crossing origin. Import into Blender reverses this conversion.

Editable objects/provenance remain in the [Blender scene](../scene/elisabethkirche.blend).
Baking samples continuous patina into repeating material patches. This is an
explicit appearance approximation; UV scales follow the same stone/slate metre
parameters. The GLB has overlapping exterior components, no functional interior
and is not a globally watertight fabrication mesh.

See the [SOL-01 report](../../validation/reports/SOL-01.md),
[reimport checks](../../validation/reports/SOL-01-glb-check.json),
[embedded-material review renders](../../validation/delivery/SOL-01/README.md)
and [asset licences/attribution](../../validation/delivery/SOL-01/LICENSE.md).
Intermediate bake PNGs are regenerated under ignored `textures/`; the delivered
GLB contains every required image.
