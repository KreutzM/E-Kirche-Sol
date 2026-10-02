"""Run on the delivered blend, independently of the construction script."""
from pathlib import Path
import json
import bpy
import bmesh

ROOT = Path(__file__).resolve().parents[2]
scene = bpy.context.scene
required = ['MASSING', 'TOWERS', 'ROOFS', 'BUTTRESSES', 'OPENINGS',
            'TRACERY', 'DETAIL', 'CAMERAS', 'REFERENCE']
assert scene.unit_settings.system == 'METRIC'
assert scene.unit_settings.scale_length == 1
assert scene['axis_convention'] == 'X east, Y north, Z up'
assert scene['origin_definition'] == 'centre of crossing at nominal floor level'
assert all(name in bpy.data.collections for name in required)
assert len(bpy.data.collections['CAMERAS'].objects) == 12
assert all(bpy.data.objects[name].type == 'CAMERA' for name in ['VAL_W','VAL_SW','VAL_S','VAL_SE','VAL_N'])
architectural = [o for name in required[:3] for o in bpy.data.collections[name].objects]
assert len(architectural) == 60
for obj in architectural:
    assert obj.type == 'MESH' and obj['parameter_keys'] and obj['evidence_ids']
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    assert all(e.is_manifold for e in bm.edges), obj.name
    bm.free()
coords = [obj.matrix_world @ v.co for obj in architectural for v in obj.data.vertices]
bounds = [[min(p[i] for p in coords), max(p[i] for p in coords)] for i in range(3)]
assert abs(bounds[2][0]) < 0.01 and abs(bounds[2][1] - 80) < 0.01, bounds
assert len([o for o in architectural if o.name.startswith('Tower_shaft_')]) == 2
result = {'iteration':scene['iteration'], 'saved_scene_reopened':True,
          'architectural_meshes':len(architectural), 'closed_individual_meshes':True,
          'required_collections':required, 'cameras':12, 'bounds_xyz_m':bounds,
          'blender_version':bpy.app.version_string}
(ROOT/'validation/reports/goal-1-reopen.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('SAVED MASSING VERIFIED', result)
