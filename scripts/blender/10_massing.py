"""Coarse massing scaffold for the independent GPT-6.1-Sol experiment.

This file creates documented scale guides only. It intentionally does not contain a reconstructed
church solution. Add architectural massing only after reading AGENTS.md and EXPERIMENT.md, and
record every inferred dimension in data/assumptions.yaml.
"""
import bpy

def collection(name):
    return bpy.data.collections[name]

def guide_cube(name, size_xyz, location=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size_xyz
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection("REFERENCE").objects.link(obj)
    obj.display_type = "WIRE"
    obj.hide_render = True
    obj["evidence_status"] = "documented scale guide; not architectural surface"
    return obj

# Documented / near-documented scale guides only.
guide_cube("REF_crossing_10m", (10.0, 10.0, 0.10), (0, 0, 0.05))
# The hall runs east-west (X); its transverse width is north-south (Y).
guide_cube("REF_hall_width_21_55m", (0.10, 21.55, 0.10), (0, 0, 0.15))
guide_cube("REF_tower_height_80m", (0.10, 0.10, 80.0), (0, 0, 40.0))

print("Created documented scale guides only; no reconstructed church geometry.")
