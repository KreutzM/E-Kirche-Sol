"""Independent fresh-process GLB import, material/bounds checks and actual renders."""
from pathlib import Path
import hashlib
import json
import math
import struct
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
GLB=ROOT/'blender/exports/elisabethkirche_SOL-01.glb'
data=GLB.read_bytes()
magic,version,length=struct.unpack_from('<4sII',data)
assert magic==b'glTF' and version==2 and length==len(data)
size,kind=struct.unpack_from('<II',data,12)
assert kind==0x4e4f534a
document=json.loads(data[20:20+size])
assert document['images'] and all('bufferView' in i and 'uri' not in i for i in document['images'])
assert len(document['images'])==6,len(document['images'])
assert all('uri' not in b for b in document['buffers'])
for m in document['materials']:
    pbr=m['pbrMetallicRoughness']
    assert 'baseColorFactor' in pbr or 'baseColorTexture' in pbr
    if any(s in m['name'] for s in ['sandstone ashlar','Slate roof','exterior glazing']):
        assert 'baseColorTexture' in pbr and 'normalTexture' in m,m['name']
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(GLB))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
export=json.loads((ROOT/'validation/reports/SOL-01-export.json').read_text())
assert len(objects)==export['export_batches'],len(objects)
assert sum(o['source_component_count'] for o in objects)==export['source_components']
assert {o['source_collection'] for o in objects}=={'MASSING','TOWERS','ROOFS','BUTTRESSES','OPENINGS','TRACERY','DETAIL'}
assert all(o.data.polygons and o.data.materials for o in objects)
assert all(math.isfinite(c) for o in objects for v in o.data.vertices for c in v.co)
coords=[o.matrix_world @ v.co for o in objects for v in o.data.vertices]
bounds=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]
original=json.loads((ROOT/'validation/reports/SOL-01-reopen.json').read_text())
assert all(abs(bounds[i][j]-original['bounds_xyz_m'][i][j])<.1 for i in range(3) for j in range(2)),bounds
assert abs(bounds[2][1]-80)<.01 and abs(bounds[2][0])<.01
materials={m for o in objects for m in o.data.materials}
textured=[]
for m in materials:
    images=[n.image for n in m.node_tree.nodes if n.type=='TEX_IMAGE']
    for image in images:
        assert image and image.size[0]==1024 and image.size[1]==1024
        assert image.packed_file or image.packed_files,image.name
    if images:textured.append(m.name)
assert len(textured)==3,textured
# Append only the stage and cameras from the delivered editable file. Architecture
# in these renders is exclusively reimported GLB geometry and embedded materials.
with bpy.data.libraries.load(str(ROOT/'blender/scene/elisabethkirche.blend'),link=False) as (source,target):
    target.collections=['CAMERAS','REFERENCE']
    target.worlds=source.worlds
for col in target.collections:bpy.context.scene.collection.children.link(col)
scene=bpy.context.scene
scene.world=target.worlds[0]
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.view_settings.view_transform='AgX'
scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
out=ROOT/'validation/delivery/SOL-01'
for name,resolution in [('PRES_SE',(2000,1800)),('VAL_W',(1200,1800))]:
    scene.camera=bpy.data.objects[name]
    scene.render.resolution_x,scene.render.resolution_y=resolution
    scene.render.filepath=str(out/(name+'_GLB.png'))
    bpy.ops.render.render(write_still=True)
frames=json.loads((ROOT/'validation/reports/SOL-01-renders.json').read_text())
for name,record in frames.items():
    image=bpy.data.images.load(str(ROOT/record['path']),check_existing=False)
    assert list(image.size)==record['resolution'] and max(image.size)>=1800,name
    bpy.data.images.remove(image)
assert len(frames)==14 and sum(r['purpose']=='presentation' for r in frames.values())==2
assert all(n in frames for n in ['VAL_W','VAL_SW','VAL_S','VAL_SE','VAL_N','VAL_NNE_ROOF','VAL_PLAN','VAL_ELEV_E'])
result={'glb_sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'fresh_process_import':True,
        'batches':len(objects),'source_components':export['source_components'],
        'vertices':sum(len(o.data.vertices) for o in objects),'triangles':sum(len(o.data.polygons) for o in objects),
        'bounds_xyz_m_after_import':bounds,'embedded_images':len(document['images']),
        'material_count':len(materials),'textured_materials':textured,
        'axis_and_metre_bounds_match_editable_scene':True,'render_files_verified':len(frames),
        'glb_review_renders':['validation/delivery/SOL-01/PRES_SE_GLB.png','validation/delivery/SOL-01/VAL_W_GLB.png'],
        'blender_version':bpy.app.version_string}
(ROOT/'validation/reports/SOL-01-glb-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('FRESH GLB IMPORT VERIFIED',result)
audit=json.loads((ROOT/'sources/reference_audit.json').read_text(encoding='utf-8'))
for record in audit['records']:
    path=ROOT/record['downloaded_to']
    # References are optional for rebuilding; when present, enforce immutability.
    if path.exists():assert hashlib.sha256(path.read_bytes()).hexdigest()==record['local_sha256'],record['id']
paths=[ROOT/'blender/scene/elisabethkirche.blend',GLB]+sorted(out.glob('*.png'))
artifacts={'iteration':'G3-01','reference_hashes_checked':sum((ROOT/r['downloaded_to']).exists() for r in audit['records']),
           'artifacts':[{'path':str(p.relative_to(ROOT)).replace('\\','/'),'bytes':p.stat().st_size,
                         'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]}
(ROOT/'validation/reports/SOL-01-artifacts.json').write_text(json.dumps(artifacts,indent=2)+'\n',encoding='utf-8')
