"""Independent coarse exterior. Every architectural size comes from input evidence."""
from pathlib import Path
import json
import math
import sys
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
INPUTS = json.loads(Path(sys.argv[sys.argv.index("--") + 1]).read_text(encoding="utf-8"))
A = INPUTS["assumptions"]
D = INPUTS["dimensions"]
P = {name: record["value"] for name, record in A.items()}
ITERATION = "G2-04" if INPUTS.get("architecture") else "G1-04"

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for col in list(bpy.data.collections):
    bpy.data.collections.remove(col)
for mat in list(bpy.data.materials):
    bpy.data.materials.remove(mat)
COLLECTIONS = ("MASSING", "TOWERS", "ROOFS", "BUTTRESSES", "OPENINGS", "TRACERY", "DETAIL", "CAMERAS", "REFERENCE")
for name in COLLECTIONS:
    bpy.context.scene.collection.children.link(bpy.data.collections.new(name))


def material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Roughness"].default_value = 0.85
    return mat


STONE = material("Massing clay — neutral warm", (0.43, 0.40, 0.35))
ROOF = material("Roof clay — neutral dark", (0.19, 0.23, 0.25))
GROUND = material("Validation ground", (0.79, 0.80, 0.81))


def tag(obj, collection, mat, keys=()):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    bpy.data.collections[collection].objects.link(obj)
    obj.data.materials.append(mat)
    obj["iteration"] = ITERATION
    obj["evidence_status"] = "inferred coarse exterior; not measured surface"
    obj["parameter_keys"] = ", ".join(keys)
    obj["evidence_ids"] = ", ".join(sorted({ident for key in keys for ident in A[key]["evidence"]}))
    return obj


def mesh(name, vertices, faces, collection="MASSING", mat=STONE, keys=()):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    tag(obj, collection, mat, keys)
    # Face winding is normalised for closed coarse volumes.
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(data)
    bm.free()
    return obj


def prism(name, points, bottom, top, collection="MASSING", mat=STONE, keys=()):
    n = len(points)
    vertices = [(x, y, bottom) for x, y in points] + [(x, y, top) for x, y in points]
    faces = [tuple(reversed(range(n))), tuple(range(n, n * 2))]
    faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    return mesh(name, vertices, faces, collection, mat, keys)


def box(name, xmin, xmax, ymin, ymax, bottom, top, collection="MASSING", mat=STONE, keys=()):
    return prism(name, [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)], bottom, top, collection, mat, keys)


def ring(cx, cy, radius, count=8, angle=math.pi / 8):
    return [(cx + radius * math.cos(angle + 2 * math.pi * i / count),
             cy + radius * math.sin(angle + 2 * math.pi * i / count)) for i in range(count)]


def taper(name, cx, cy, radius, tip_radius, bottom, top, collection="TOWERS", mat=STONE, keys=()):
    lower, upper = ring(cx, cy, radius), ring(cx, cy, tip_radius)
    if tip_radius == 0:
        return mesh(name, [(x, y, bottom) for x, y in lower] + [(cx, cy, top)],
                    [tuple(reversed(range(8)))] + [(i, (i + 1) % 8, 8) for i in range(8)],
                    collection, mat, keys)
    vertices = [(x, y, bottom) for x, y in lower] + [(x, y, top) for x, y in upper]
    faces = [tuple(reversed(range(8))), tuple(range(8, 16))]
    faces += [(i, (i + 1) % 8, (i + 1) % 8 + 8, i + 8) for i in range(8)]
    return mesh(name, vertices, faces, collection, mat, keys)


def xy(u, v, direction):
    return (u, v) if direction == "E" else ((-v, u) if direction == "N" else (v, -u))


def gable_roof(name, xmin, xmax, half_width, bottom, top, direction="E", center=(0, 0), keys=()):
    local = [(xmin, -half_width, bottom), (xmax, -half_width, bottom),
             (xmax, half_width, bottom), (xmin, half_width, bottom),
             (xmin, 0, top), (xmax, 0, top)]
    vertices = []
    for u, v, z in local:
        x, y = xy(u, v, direction)
        vertices.append((x + center[0], y + center[1], z))
    return mesh(name, vertices, [(0, 3, 2, 1), (0, 1, 5, 4), (3, 4, 5, 2), (0, 4, 3), (1, 2, 5)], "ROOFS", ROOF, keys)


# 1: footprint; 2: hall/triconch; inferred exterior, distinct from scale guides.
h = P["arm_half_width"]
cap = P["conch_cap_center"]
eave = P["wall_eave_height"]
ridge = P["main_roof_ridge"]
nave_west = P["nave_west_end"]
hall_half = P["hall_exterior_width"] / 2
body_keys = ("arm_half_width", "conch_cap_center", "wall_eave_height", "conch_facets")
local_cap = [(cap + h * math.cos(-math.pi / 2 + i * math.pi / int(P["conch_facets"])),
              h * math.sin(-math.pi / 2 + i * math.pi / int(P["conch_facets"])))
             for i in range(int(P["conch_facets"]) + 1)]
outline = [(-h, -h)] + local_cap + [(-h, h)]
for direction in ("E", "N", "S"):
    prism("Conch_" + direction, [xy(u, v, direction) for u, v in outline], 0, eave, keys=body_keys)
box("Hall_exterior", nave_west, -h, -hall_half, hall_half, 0, eave,
    keys=("nave_west_end", "arm_half_width", "hall_exterior_width", "wall_eave_height"))
sx0, sx1, sy0, sy1 = [P[key] for key in ("sacristy_x_min", "sacristy_x_max", "sacristy_y_min", "sacristy_y_max")]
sac_keys = ("sacristy_x_min", "sacristy_x_max", "sacristy_y_min", "sacristy_y_max", "sacristy_eave")
box("Sacristy_NE", sx0, sx1, sy0, sy1, 0, P["sacristy_eave"], keys=sac_keys)
prism("North_reentrant_stair", ring(P["north_stair_center_x"], P["north_stair_center_y"], P["north_stair_radius"], 16),
      0, P["north_stair_top"], keys=("north_stair_center_x", "north_stair_center_y", "north_stair_radius", "north_stair_top"))

# 3: western towers, primary stepped corner masses and upper stone helms.
tx = P["west_tower_center_x"]
tw = P["west_tower_core_width"] / 2
td = P["west_tower_core_depth"] / 2
tkeys = ("west_tower_center_x", "west_tower_center_y", "west_tower_core_width", "west_tower_core_depth", "west_tower_shoulder")
for side in (-1, 1):
    ty = side * P["west_tower_center_y"]
    suffix = "S" if side == -1 else "N"
    box("Tower_shaft_" + suffix, tx - td, tx + td, ty - tw, ty + tw, 0, P["west_tower_shoulder"], "TOWERS", keys=tkeys)
    radius = P["west_tower_octagon_radius"]
    prism("Tower_upper_octagon_" + suffix, ring(tx, ty, radius), P["west_tower_shoulder"], P["west_tower_spire_base"], "TOWERS",
          keys=("west_tower_center_x", "west_tower_center_y", "west_tower_octagon_radius", "west_tower_shoulder", "west_tower_spire_base"))
    taper("Tower_stone_helm_" + suffix, tx, ty, radius, P["spire_tip_radius"], P["west_tower_spire_base"],
          D["tower_height"]["value"] - P["finial_extent"], keys=("west_tower_center_x", "west_tower_center_y", "west_tower_octagon_radius", "spire_tip_radius", "west_tower_spire_base", "finial_extent"))
    taper("Tower_terminal_" + suffix, tx, ty, P["finial_extent"] / 2, 0, D["tower_height"]["value"] - P["finial_extent"], D["tower_height"]["value"],
          keys=("west_tower_center_x", "west_tower_center_y", "finial_extent"))
    for xsign in (-1, 1):
        for ysign in (-1, 1):
            # Two crossed projecting rectangular masses per corner, not decoration.
            for along in ("X", "Y"):
                width, depth = P["corner_support_width"], P["corner_support_depth"]
                tiers = [(0, P["corner_support_first_step"], 1),
                         (P["corner_support_first_step"], P["corner_support_second_step"], P["corner_support_mid_factor"]),
                         (P["corner_support_second_step"], P["west_tower_shoulder"], P["corner_support_top_factor"])]
                for index, (z0, z1, factor) in enumerate(tiers):
                    cx = tx + xsign * (td + depth * factor / 2 - width / 2) if along == "X" else tx + xsign * (td - width / 2)
                    cy = ty + ysign * (tw - width / 2) if along == "X" else ty + ysign * (tw + depth * factor / 2 - width / 2)
                    dx, dy = (depth * factor + width, width) if along == "X" else (width, depth * factor + width)
                    box(f"Tower_corner_{suffix}_{xsign}_{ysign}_{along}_{index}", cx - dx / 2, cx + dx / 2, cy - dy / 2, cy + dy / 2,
                        z0, z1, "TOWERS", keys=tkeys + ("corner_support_width", "corner_support_depth", "corner_support_first_step", "corner_support_second_step", "corner_support_mid_factor", "corner_support_top_factor"))
            px, py = tx + xsign * (td - P["upper_pinnacle_width"] / 2), ty + ysign * (tw - P["upper_pinnacle_width"] / 2)
            pw = P["upper_pinnacle_width"] / 2
            box(f"Corner_turret_{suffix}_{xsign}_{ysign}", px - pw, px + pw, py - pw, py + pw,
                P["west_tower_shoulder"], P["upper_pinnacle_shaft_top"], "TOWERS", keys=tkeys + ("upper_pinnacle_width", "upper_pinnacle_shaft_top"))
            taper(f"Corner_turret_tip_{suffix}_{xsign}_{ysign}", px, py, pw, 0, P["upper_pinnacle_shaft_top"], P["upper_pinnacle_top"], keys=tkeys + ("upper_pinnacle_width", "upper_pinnacle_shaft_top", "upper_pinnacle_top"))
# Union the primary supports with their shaft to remove duplicate coplanar caps.
# Geometry changes here fix a rendering/topology defect, not a photographic mismatch.
for suffix in ("S", "N"):
    shaft = bpy.data.objects["Tower_shaft_" + suffix]
    supports = [obj for obj in bpy.data.objects if obj.name.startswith("Tower_corner_" + suffix + "_")]
    for support in supports:
        bpy.context.view_layer.objects.active = shaft
        modifier = shaft.modifiers.new("Union_primary_corner_volume", "BOOLEAN")
        modifier.operation = "UNION"
        modifier.solver = "EXACT"
        modifier.object = support
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.data.objects.remove(support, do_unlink=True)
    extra_keys = ("corner_support_width", "corner_support_depth", "corner_support_first_step", "corner_support_second_step", "corner_support_mid_factor", "corner_support_top_factor")
    shaft["parameter_keys"] = ", ".join(tkeys + extra_keys)
    shaft["evidence_ids"] = ", ".join(sorted({ident for key in tkeys + extra_keys for ident in A[key]["evidence"]}))
half_gap = P["west_tower_center_y"] - tw
# Only fill the inter-tower gap: spanning the cores creates coplanar double walls.
box("West_hall_bridge", tx - td - P["west_front_depth"], nave_west, -half_gap, half_gap, 0, eave, keys=tkeys + ("nave_west_end", "wall_eave_height", "west_front_depth"))

# Central west gable, a coarse plate rather than the later ornamental stepped front.
front = tx - td
vertices = [(front - P["west_front_depth"], -half_gap, eave), (front - P["west_front_depth"], half_gap, eave), (front - P["west_front_depth"], 0, P["west_gable_top"]),
            (front, -half_gap, eave), (front, half_gap, eave), (front, 0, P["west_gable_top"])]
mesh("West_central_gable", vertices, [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)], "TOWERS", STONE,
     tkeys + ("west_gable_top", "west_front_depth", "wall_eave_height"))

# 4: longitudinal nave ridge, lower transverse aisle roofs, three polygonal hips.
roof_bottom = eave - P["roof_base_inset"]
rh = h + P["roof_overhang"]
roof_keys = body_keys + ("main_roof_ridge", "roof_overhang", "roof_base_inset")
# 1 mm is a computational anti-coplanarity tolerance, not an architectural size.
gable_roof("Nave_main_roof", front + 0.001, 0, rh, roof_bottom, ridge,
           keys=roof_keys + ("west_tower_center_x", "west_tower_core_depth"))
for direction in ("E", "N", "S"):
    gable_roof("Conch_barrel_roof_" + direction, 0, cap, rh, roof_bottom, ridge, direction, keys=roof_keys)
    arc = [(cap + rh * math.cos(-math.pi / 2 + i * math.pi / int(P["conch_facets"])),
            rh * math.sin(-math.pi / 2 + i * math.pi / int(P["conch_facets"]))) for i in range(int(P["conch_facets"]) + 1)]
    transformed = [xy(u, v, direction) for u, v in arc]
    apex = xy(cap, 0, direction)
    n = len(arc)
    mesh("Conch_polygon_hip_" + direction, [(x, y, roof_bottom) for x, y in transformed] + [(apex[0], apex[1], ridge)],
         [tuple(reversed(range(n)))] + [(i, i + 1, n) for i in range(n - 1)] + [(n - 1, 0, n)], "ROOFS", ROOF, roof_keys)
count = int(P["side_roof_count"])
bay = (-h - nave_west) / count
for side in (-1, 1):
    for index in range(count):
        cx = nave_west + (index + 0.5) * bay
        # Local u is north-south: ridge runs across the aisle from facade to main roof.
        gable_roof(f"Aisle_transverse_roof_{side}_{index}", P["side_roof_inner_edge"], hall_half + P["roof_overhang"], bay / 2,
                   roof_bottom, P["side_roof_ridge"], "N" if side > 0 else "S", (cx, 0),
                   keys=("nave_west_end", "arm_half_width", "hall_exterior_width", "side_roof_count", "side_roof_ridge", "side_roof_inner_edge", "wall_eave_height", "roof_overhang", "roof_base_inset"))
# Pyramid on rectangular NE annex.
mesh("Sacristy_pyramidal_roof", [(sx0, sy0, P["sacristy_eave"]), (sx1, sy0, P["sacristy_eave"]),
     (sx1, sy1, P["sacristy_eave"]), (sx0, sy1, P["sacristy_eave"]),
     ((sx0 + sx1) / 2, (sy0 + sy1) / 2, P["sacristy_roof_top"])],
     [(0, 3, 2, 1), (0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)], "ROOFS", ROOF, sac_keys + ("sacristy_roof_top",))

# Modern roof rider: closed octagonal foot, open lantern, slender slate spire.
rr = P["roof_rider_radius"]
rider_keys = ("roof_rider_radius", "roof_rider_body_top", "roof_rider_lantern_top", "roof_rider_top", "roof_rider_post_width", "roof_rider_trim", "main_roof_ridge")
prism("Crossing_rider_base", ring(0, 0, rr), ridge, P["roof_rider_body_top"], "ROOFS", ROOF, rider_keys)
for index, (x, y) in enumerate(ring(0, 0, rr)):
    pw = P["roof_rider_post_width"] / 2
    box(f"Crossing_lantern_post_{index}", x - pw, x + pw, y - pw, y + pw, P["roof_rider_body_top"], P["roof_rider_lantern_top"], "ROOFS", ROOF, rider_keys)
taper("Crossing_rider_spire", 0, 0, rr + P["roof_rider_trim"], 0, P["roof_rider_lantern_top"], P["roof_rider_top"], "ROOFS", ROOF, rider_keys)

if INPUTS.get("architecture"):
    import runpy
    runpy.run_path(str(ROOT / "scripts/blender/30_exterior_architecture.py"))["build"](globals())

# Non-architectural validation stage; its sizes are presentation settings.
box("Validation_ground", -160, 160, -160, 160, -0.20, -0.02, "REFERENCE", GROUND)
bpy.data.objects["Validation_ground"]["evidence_status"] = "presentation ground only"
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.length_unit = "METERS"
scene.unit_settings.scale_length = 1
scene["project"] = "Elisabethkirche Marburg — independent exterior massing"
scene["axis_convention"] = "X east, Y north, Z up"
scene["origin_definition"] = "centre of crossing at nominal floor level"
scene["iteration"] = ITERATION
scene["quality_stage"] = "Goal 2 developed exterior" if INPUTS.get("architecture") else "Goal 1 coarse massing, openings/detail/material finish pending Goal 2"
scene.render.engine = "CYCLES"
scene.cycles.samples = 48 if INPUTS.get("architecture") else 32
scene.cycles.use_denoising = True
scene.world.color = (0.65, 0.65, 0.65)
scene.world.use_nodes = True
scene.world.node_tree.nodes.get("Background").inputs[0].default_value = (0.8, 0.8, 0.8, 1)
scene.world.node_tree.nodes.get("Background").inputs[1].default_value = 0.4
scene.view_settings.view_transform = "AgX"
light_data = bpy.data.lights.new("Neutral_key", "SUN")
light_data.energy = 2
light_data.angle = math.radians(20)
light = bpy.data.objects.new("Neutral_key", light_data)
bpy.data.collections["REFERENCE"].objects.link(light)
light.rotation_euler = (math.radians(25), math.radians(-30), math.radians(-25))

for name, config in INPUTS["cameras"]["cameras"].items():
    data = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, data)
    bpy.data.collections["CAMERAS"].objects.link(cam)
    cam.location = config["position"]
    direction = Vector(config["target"]) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    if config.get("roll_deg"):
        from mathutils import Quaternion
        cam.rotation_euler = (cam.rotation_euler.to_quaternion() @ Quaternion((0, 0, 1), math.radians(config["roll_deg"]))).to_euler()
    data.type = config.get("type", "PERSP")
    data.lens = config.get("lens_mm", 35)
    data.sensor_width = 36
    data.sensor_fit = "HORIZONTAL"
    data.clip_end = 1000
    data.ortho_scale = config.get("ortho_scale", 100)
    cam["evidence_ids"] = ", ".join(config.get("evidence", []))
    cam["fit_status"] = config["status"]
    cam["iteration"] = config["iteration"]

scene.camera = bpy.data.objects["VAL_SE"]
scene.render.image_settings.file_format = "PNG"
scene.render.resolution_x, scene.render.resolution_y = 1400, 1156
scene.render.resolution_percentage = 100
SCENE = ROOT / "blender/scene/elisabethkirche.blend"
SCENE.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SCENE))

# Validate generated bounds, collection membership, provenance and closed meshes.
import bmesh
checks = []
for collection in ("MASSING", "TOWERS", "ROOFS"):
    objects = list(bpy.data.collections[collection].objects)
    assert objects, collection
    for obj in objects:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bad_edges = sum(not edge.is_manifold for edge in bm.edges)
        bm.free()
        assert bad_edges == 0, (obj.name, bad_edges)
        assert obj["parameter_keys"], obj.name
    checks.append({"collection": collection, "objects": len(objects), "closed_individual_meshes": True})
tip = cap + h * math.cos(math.pi / 10)
metrics = {"tower_tip_height": D["tower_height"]["value"], "exterior_hall_width": 2 * hall_half,
           "interior_hall_proxy": 2 * hall_half - 2 * P["hall_wall_zone"],
           "interior_transept_proxy": 2 * (tip - P["conch_wall_zone"]),
           "interior_length_without_west_hall_proxy": tip - P["conch_wall_zone"] - nave_west,
           "crossing_pitch_inferred": P["crossing_structural_pitch"], "wall_eave": eave, "main_roof_ridge": ridge,
           "collections": checks, "cameras": len(INPUTS["cameras"]["cameras"]), "iteration": ITERATION,
           "warning": "Interior proxies are rough scale cross-checks on solid massing, not measured or modeled interior surfaces."}
for key, anchor in (("interior_hall_proxy", "hall_total_width"), ("interior_transept_proxy", "transept_width"), ("interior_length_without_west_hall_proxy", "inner_length_without_west_hall")):
    assert abs(metrics[key] - D[anchor]["value"]) / D[anchor]["value"] < 0.05, (key, metrics[key])
report_dir = ROOT / "validation/reports"
report_dir.mkdir(parents=True, exist_ok=True)
(report_dir / ("goal-2-build.json" if INPUTS.get("architecture") else "goal-1-build.json")).write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
print("MASSING CHECKS OK", metrics)
if INPUTS["render"]:
    output = ROOT / "validation/renders" / ITERATION
    output.mkdir(parents=True, exist_ok=True)
    for name, config in INPUTS["cameras"]["cameras"].items():
        if INPUTS.get("views") and name not in INPUTS["views"]:
            continue
        scene.camera = bpy.data.objects[name]
        scene.render.resolution_x, scene.render.resolution_y = config.get("resolution", [1400, 1100])
        scene.render.filepath = str(output / f"{name}.png")
        bpy.ops.render.render(write_still=True)
        print("RENDERED", scene.render.filepath)
