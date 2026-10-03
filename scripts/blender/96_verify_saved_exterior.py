"""Verify delivered Goal-2 scene, including actual niche depth and camera stability."""
from pathlib import Path
import json
import math
import bpy
import bmesh
from mathutils import Vector, Quaternion

ROOT = Path(__file__).resolve().parents[2]
scene = bpy.context.scene
required = ['MASSING','TOWERS','ROOFS','BUTTRESSES','OPENINGS','TRACERY','DETAIL','CAMERAS','REFERENCE']
assert scene.unit_settings.system == 'METRIC' and scene.unit_settings.scale_length == 1
assert scene['axis_convention'] == 'X east, Y north, Z up'
assert scene['origin_definition'] == 'centre of crossing at nominal floor level'
assert scene['iteration'].startswith(('G2-', 'G3-'))
for name in required:
    assert name in bpy.data.collections
    if name!='REFERENCE':assert bpy.data.collections[name].objects, name
objects=[o for name in required[:7] for o in bpy.data.collections[name].objects]
mesh_count=curve_count=0
for obj in objects:
    assert obj['parameter_keys'] and obj['evidence_ids'],obj.name
    if obj.type=='MESH':
        mesh_count+=1
        assert all(math.isfinite(c) for v in obj.data.vertices for c in v.co),obj.name
        bm=bmesh.new();bm.from_mesh(obj.data)
        bad=[e for e in bm.edges if not e.is_manifold];bm.free()
        assert not bad,(obj.name,len(bad))
        assert obj.data.materials and obj.data.uv_layers,obj.name
    elif obj.type=='CURVE':
        curve_count+=1
        assert obj.data.bevel_depth>0 and obj.data.use_fill_caps,obj.name
    else:raise AssertionError((obj.name,obj.type))
assert len([o for o in objects if o.name.startswith('Tower_shaft_')])==2
coords=[obj.matrix_world @ v.co for obj in objects if obj.type=='MESH' for v in obj.data.vertices]
bounds=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]
assert abs(bounds[2][0])<.01 and abs(bounds[2][1]-80)<.01,bounds
config=json.loads((ROOT/'validation/cameras.json').read_text(encoding='utf-8'))['cameras']
validation_cameras=[o for o in bpy.data.collections['CAMERAS'].objects if o.name.startswith('VAL_')]
assert len(validation_cameras)==len(config)==12
for name,c in config.items():
    obj=bpy.data.objects[name]
    assert (obj.location-Vector(c['position'])).length<1e-4,(name,'camera moved')
    assert abs(obj.data.lens-c.get('lens_mm',35))<1e-4,name
    direction=(Vector(c['target'])-obj.location).normalized()
    actual=obj.rotation_euler.to_quaternion() @ Vector((0,0,-1))
    assert actual.dot(direction)>.99999,name
    expected=direction.to_track_quat('-Z','Y') @ Quaternion((0,0,1),math.radians(c.get('roll_deg',0)))
    # q and -q encode exactly the same rotation; Euler round trips may flip sign.
    actual_quat=obj.rotation_euler.to_quaternion().normalized()
    assert abs(expected.normalized().dot(actual_quat))>.999999,(name,'camera roll changed')
    assert obj.data.type==c.get('type','PERSP') and obj.data.sensor_fit=='HORIZONTAL',name
    assert abs(obj.data.sensor_width-36)<1e-4,name
    assert abs(obj.data.ortho_scale-c.get('ortho_scale',100))<1e-4,name
presentation_count=0
if scene['iteration'].startswith('G3-'):
    presentation=json.loads((ROOT/'validation/presentation_cameras.json').read_text(encoding='utf-8'))['cameras']
    assert {o.name for o in bpy.data.collections['CAMERAS'].objects if o.name.startswith('PRES_')}==set(presentation)
    for name,c in presentation.items():
        obj=bpy.data.objects[name]
        assert (obj.location-Vector(c['position'])).length<1e-4,name
        assert abs(obj.data.lens-c['lens_mm'])<1e-4,name
        assert obj['fit_status']=='presentation only; no source-photo solution',name
    presentation_count=len(presentation)
# Rays into a known regular nave opening: host wall alone must have a blind
# recess, while the separate glass lies in front of its rear stone surface.
hall=bpy.data.objects['Hall_exterior'];width=23.95/2
bay=(-6.4-(-36))/5;x=-36+bay*.5
origin=Vector((x+.35,-width-2,5));direction=Vector((0,1,0))
hit,location,normal,face=hall.ray_cast(origin,direction)
assert hit and abs(location.y-(-width+.42))<.01,('actual niche depth',location)
glass=bpy.data.objects['Window_Hall_-1_0_lower_glazing']
hit,glass_location,normal,face=glass.ray_cast(origin,direction)
assert hit and glass_location.y<location.y,('glass behind wall',glass_location,location)
assert 'West_clock_glazing_glazing' in bpy.data.objects
assert 'West_red_double_doors' in bpy.data.objects
assert 'West_clock_open_dial' in bpy.data.objects
assert 'Stair_slate_cap' in bpy.data.objects
assert not any('_CUT' in o.name for o in bpy.data.objects),'temporary cutter retained'
result={'iteration':scene['iteration'],'saved_scene_reopened':True,
        'mesh_count':mesh_count,'profile_curve_count':curve_count,'closed_individual_meshes':True,
        'bounds_xyz_m':bounds,'camera_configs_unchanged':True,
        'presentation_cameras_verified':presentation_count,
        'sample_niche_depth_m':round(location.y+width,4),'sample_glass_in_front_of_niche_back':True,
        'collections':{name:len(bpy.data.collections[name].objects) for name in required},
        'blender_version':bpy.app.version_string}
report='SOL-01-reopen.json' if scene['iteration'].startswith('G3-') else 'goal-2-reopen.json'
(ROOT/'validation/reports'/report).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('SAVED EXTERIOR VERIFIED',result)
