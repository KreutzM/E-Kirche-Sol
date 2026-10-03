"""SOL-01 presentation and portable material export. No new inferred geometry.

Bake reusable material swatches from the existing procedural shaders, rescale
metre UVs only in the export copy, convert curves and batch by collection/material.
The editable scene keeps its original shaders, individual objects and coordinates.
"""
import json
from pathlib import Path
import bpy
from mathutils import Vector

ARCHITECTURE = ('MASSING','TOWERS','ROOFS','BUTTRESSES','OPENINGS','TRACERY','DETAIL')


def bake_material(source, extent, folder, size=1024):
    """Base colour and tangent normal swatch; unlit colour, no baked shadows."""
    original_scene = bpy.context.window.scene
    scene = bpy.data.scenes.new('Temporary_material_bake')
    bpy.context.window.scene = scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 16
    scene.render.bake.margin = 8
    w,h = extent
    mesh = bpy.data.meshes.new('Bake_plane')
    mesh.from_pydata([(0,0,0),(w,0,0),(w,h,0),(0,h,0)],[],[(0,1,2,3)])
    obj = bpy.data.objects.new('Bake_plane',mesh)
    scene.collection.objects.link(obj)
    metres = mesh.uv_layers.new(name='SurfaceMetres')
    uv = mesh.uv_layers.new(name='BakeUV')
    for i,co in enumerate([(0,0),(1,0),(1,1),(0,1)]):
        uv.data[i].uv = co
        metres.data[i].uv = (co[0]*w,co[1]*h)
    mesh.uv_layers.active = uv
    uv.active_render = True
    material = source.copy()
    mesh.materials.append(material)
    nodes,links = material.node_tree.nodes,material.node_tree.links
    named = nodes.new('ShaderNodeUVMap');named.uv_map='SurfaceMetres'
    for node in list(nodes):
        if node.type=='TEX_COORD':
            for link in list(node.outputs['UV'].links):
                links.new(named.outputs['UV'],link.to_socket)
    bs = nodes.get('Principled BSDF')
    output = next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
    emitter = nodes.new('ShaderNodeEmission')
    color = bs.inputs['Base Color']
    if color.is_linked:links.new(color.links[0].from_socket,emitter.inputs['Color'])
    else:emitter.inputs['Color'].default_value = color.default_value
    links.new(emitter.outputs[0],output.inputs['Surface'])
    bpy.context.view_layer.objects.active=obj;obj.select_set(True)
    baked={}
    for kind,bake_type in [('basecolor','EMIT'),('normal','NORMAL')]:
        if kind=='normal':links.new(bs.outputs[0],output.inputs['Surface'])
        image=bpy.data.images.new(source.name+'_'+kind,width=size,height=size,alpha=False)
        image.colorspace_settings.name='sRGB' if kind=='basecolor' else 'Non-Color'
        target=nodes.new('ShaderNodeTexImage');target.image=image
        nodes.active=target
        bpy.ops.object.bake(type=bake_type)
        safe=source.name.split(' — ')[0].replace(' ','_')
        path=folder/(safe+'_'+kind+'.png')
        image.filepath_raw=str(path);image.file_format='PNG';image.save()
        baked[kind]=image
    bpy.context.window.scene=original_scene
    bpy.data.scenes.remove(scene)
    bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.meshes.remove(mesh)
    bpy.data.materials.remove(material)
    return baked


def export_model(root, scene, parameters):
    folder=root/'blender/exports';folder.mkdir(parents=True,exist_ok=True)
    textures=folder/'textures';textures.mkdir(exist_ok=True)
    # Repeat patches span integer brick courses. World-space mottling is sampled,
    # so GLB patina repeats instead of following the entire building continuously.
    swatches={
        'Weathered sandstone ashlar — metre courses':(parameters['stone_block_width']*8,parameters['stone_course_height']*12),
        'Slate roof — staggered metre scale courses':(parameters['roof_tile_width']*8,parameters['roof_tile_exposed_height']*12),
        'Weathered blue grey exterior glazing':(2,2),
    }
    originals=[o for name in ARCHITECTURE for o in bpy.data.collections[name].objects]
    materials={m.name:m for o in originals for m in o.data.materials}
    portable={};extents={}
    for name,source in materials.items():
        bs=source.node_tree.nodes.get('Principled BSDF')
        mat=bpy.data.materials.new('GLB_'+name);mat.use_nodes=True
        shader=mat.node_tree.nodes.get('Principled BSDF')
        for key in ('Base Color','Roughness','Metallic'):
            shader.inputs[key].default_value=bs.inputs[key].default_value
        mat.diffuse_color=source.diffuse_color
        if name in swatches:
            baked=bake_material(source,swatches[name],textures)
            nodes,links=mat.node_tree.nodes,mat.node_tree.links
            tex=nodes.new('ShaderNodeTexImage');tex.image=baked['basecolor'];tex.extension='REPEAT'
            links.new(tex.outputs['Color'],shader.inputs['Base Color'])
            normal_tex=nodes.new('ShaderNodeTexImage');normal_tex.image=baked['normal'];normal_tex.extension='REPEAT'
            normal=nodes.new('ShaderNodeNormalMap')
            links.new(normal_tex.outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],shader.inputs['Normal'])
            extents[name]=swatches[name]
        portable[name]=mat
    deps=bpy.context.evaluated_depsgraph_get()
    export_scene=bpy.data.scenes.new('Temporary_GLB_export')
    bpy.context.window.scene=export_scene
    export_scene.unit_settings.system='METRIC';export_scene.unit_settings.scale_length=1
    groups={}
    for source in originals:
        collection=source.users_collection[0].name
        evaluated=source.evaluated_get(deps)
        mesh=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=deps)
        obj=bpy.data.objects.new(source.name,mesh);export_scene.collection.objects.link(obj)
        obj.matrix_world=source.matrix_world.copy()
        name=source.data.materials[0].name
        mesh.materials.clear();mesh.materials.append(portable[name])
        if name in extents:
            assert mesh.uv_layers,source.name
            uv=mesh.uv_layers.active
            for datum in uv.data:
                datum.uv=(datum.uv.x/extents[name][0],datum.uv.y/extents[name][1])
        groups.setdefault((collection,name),[]).append(obj)
    for (collection,name),objects in groups.items():
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects:obj.select_set(True)
        bpy.context.view_layer.objects.active=objects[0]
        bpy.ops.object.join()
        combined=bpy.context.object
        combined.name=collection+'__'+name
        combined['source_collection']=collection
        combined['source_component_count']=len(objects)
        combined['evidence_status']='independent inferred exterior; source parameters in repository'
    path=folder/'elisabethkirche_SOL-01.glb'
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',export_yup=True,
                              use_active_scene=True,
                              export_extras=True,export_materials='EXPORT',export_cameras=False,
                              export_lights=False,export_animations=False)
    metrics={'file':str(path.relative_to(root)).replace('\\','/'),'source_components':len(originals),
             'export_batches':len(groups),'materials':list(materials),'texture_swatches_metres':swatches,
             'embedded_textures':6,'axis_conversion':'glTF Y up; Blender (x,y,z) -> (x,z,-y)',
             'excluded':['validation ground','cameras','lights'],
             'material_limit':'Baked repeating patina/glass swatches approximate continuous procedural shading; geometry and metre UV scale retained.'}
    (root/'validation/reports/SOL-01-export.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf-8')
    bpy.context.window.scene=scene
    for obj in list(export_scene.objects):
        mesh=obj.data;bpy.data.objects.remove(obj,do_unlink=True)
        if mesh.users==0:bpy.data.meshes.remove(mesh)
    bpy.data.scenes.remove(export_scene)
    for mat in portable.values():
        if mat.users==0:bpy.data.materials.remove(mat)
    return path


def deliver(g):
    root,scene=g['ROOT'],g['scene']
    output=root/'validation/delivery/SOL-01';output.mkdir(parents=True,exist_ok=True)
    scene['quality_stage']='SOL-01 final independent exterior; documented visual approximations'
    scene['delivery_report']='validation/reports/SOL-01.md'
    scene['geometry_baseline']='G2-04; unchanged architecture in G3-01'
    scene.cycles.samples=64
    settings=json.loads((root/'validation/presentation_cameras.json').read_text(encoding='utf-8'))
    for name,c in settings['cameras'].items():
        data=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,data)
        bpy.data.collections['CAMERAS'].objects.link(cam)
        cam.location=c['position'];cam.rotation_euler=(Vector(c['target'])-cam.location).to_track_quat('-Z','Y').to_euler()
        data.lens=c['lens_mm'];data.clip_end=1000
        cam['fit_status']='presentation only; no source-photo solution'
        cam['iteration']='G3-01'
    frames={}
    for name,c in {**g['INPUTS']['cameras']['cameras'],**settings['cameras']}.items():
        scene.camera=bpy.data.objects[name]
        resolution=c.get('resolution',[1800,1600])
        factor=max(1,1800/max(resolution))
        scene.render.resolution_x=round(resolution[0]*factor)
        scene.render.resolution_y=round(resolution[1]*factor)
        scene.render.filepath=str(output/(name+'.png'))
        bpy.ops.render.render(write_still=True)
        frames[name]={'path':str(Path(scene.render.filepath).relative_to(root)).replace('\\','/'),
                      'resolution':[scene.render.resolution_x,scene.render.resolution_y],
                      'purpose':'presentation' if name.startswith('PRES_') else 'neutral validation'}
    # Same neutral stage for presentations; no cosmetic lighting masks defects.
    scene.camera=bpy.data.objects['PRES_SE']
    scene.render.filepath='//../../validation/delivery/SOL-01/PRES_SE.png'
    scene.render.resolution_x,scene.render.resolution_y=settings['cameras']['PRES_SE']['resolution']
    bpy.ops.wm.save_as_mainfile(filepath=str(g['SCENE']))
    glb=export_model(root,scene,g['P'])
    (root/'validation/reports/SOL-01-renders.json').write_text(json.dumps(frames,indent=2)+'\n',encoding='utf-8')
    print('FINAL DELIVERY BUILT',glb,len(frames),'renders')
