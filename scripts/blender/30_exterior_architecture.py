"""Goal-2 exterior; independently inferred from this repo's original references.

Called by the coarse generator after its massing gate. Dimensions are canonical
assumptions; procedural tessellation, shader colours and numerical tolerances are
render/construction settings. No external texture or sibling reconstruction used.
"""
import math
from collections import defaultdict
import bpy
from mathutils import Vector


def build(g):
    P, A = g['P'], g['A']
    mesh, prism, box, ring, taper = [g[k] for k in ('mesh','prism','box','ring','taper')]
    stone, slate = g['STONE'], g['ROOF']
    cutters = defaultdict(list)
    windows = []
    architectural_keys = tuple(k for k in A if not k.startswith('camera_'))

    def mat(name, color, roughness=0.8, metal=0):
        m = g['material'](name, color)
        bs = m.node_tree.nodes.get('Principled BSDF')
        bs.inputs['Roughness'].default_value = roughness
        bs.inputs['Metallic'].default_value = metal
        return m

    trim = mat('Dressed sandstone mouldings', (.40,.31,.23))
    dark = mat('Recess shadow / belfry interior', (.018,.023,.025))
    glass = mat('Weathered blue grey exterior glazing', (.095,.16,.185), .28, .25)
    iron = mat('Blackened iron leadwork', (.035,.044,.047), .45, .65)
    lead = mat('Weathered lead and copper flashings', (.16,.22,.20), .52, .7)
    wood = mat('West portal red painted timber', (.22,.022,.018), .7)
    relief = mat('Portal red sandstone low relief', (.34,.16,.10))

    def brick_material(m, colors, width, height, joint, bump_depth, roof=False):
        nt = m.node_tree; nodes, links = nt.nodes, nt.links
        bs = nodes.get('Principled BSDF')
        tc = nodes.new('ShaderNodeTexCoord')
        brick = nodes.new('ShaderNodeTexBrick')
        brick.offset = .5; brick.offset_frequency = 2
        for socket, value in [('Color1',(*colors[0],1)),('Color2',(*colors[1],1)),
                              ('Mortar',(*colors[2],1)),('Scale',1),('Mortar Size',joint),
                              ('Mortar Smooth',.01),('Brick Width',width),('Row Height',height)]:
            brick.inputs[socket].default_value=value
        links.new(tc.outputs['UV'],brick.inputs['Vector'])
        noise = nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=8
        noise.inputs['Detail'].default_value=3
        links.new(tc.outputs['UV'],noise.inputs['Vector'])
        mix = nodes.new('ShaderNodeMixRGB'); mix.blend_type='MULTIPLY'
        mix.inputs[0].default_value=.12
        links.new(brick.outputs['Color'],mix.inputs[1]);links.new(noise.outputs['Fac'],mix.inputs[2])
        links.new(mix.outputs[0],bs.inputs['Base Color'])
        # Broad mottled patina breaks the pristine block pattern seen in the
        # first pass. It follows world space rather than restarting per face.
        geo=nodes.new('ShaderNodeNewGeometry');patina=nodes.new('ShaderNodeTexNoise')
        patina.inputs['Scale'].default_value=.34;patina.inputs['Detail'].default_value=4
        links.new(geo.outputs['Position'],patina.inputs['Vector'])
        weather=nodes.new('ShaderNodeMixRGB');weather.blend_type='MULTIPLY'
        weather.inputs[0].default_value=.4
        links.new(mix.outputs[0],weather.inputs[1]);links.new(patina.outputs['Fac'],weather.inputs[2])
        links.new(weather.outputs[0],bs.inputs['Base Color'])
        bump=nodes.new('ShaderNodeBump');bump.inputs['Distance'].default_value=bump_depth
        bump.inputs['Strength'].default_value=.45
        links.new(brick.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],bs.inputs['Normal'])
        bs.inputs['Roughness'].default_value=.75 if roof else .88
        m['texture_units']='metre-projected UV; dimensions from assumptions'
        m['evidence_ids']='M17, M18' if roof else 'M05, M09, M16'

    stone.name='Weathered sandstone ashlar — metre courses'
    slate.name='Slate roof — staggered metre scale courses'
    brick_material(stone,[(.27,.23,.19),(.40,.33,.27),(.26,.25,.22)],
                   P['stone_block_width'],P['stone_course_height'],P['stone_joint'],P['stone_bump_depth'])
    brick_material(slate,[(.095,.12,.125),(.13,.155,.16),(.055,.065,.07)],
                   P['roof_tile_width'],P['roof_tile_exposed_height'],P['roof_tile_joint'],P['roof_bump_depth'],True)
    # Fine irregular lead network is a material approximation, not measured glazing.
    nt=glass.node_tree;tc=nt.nodes.new('ShaderNodeTexCoord');vor=nt.nodes.new('ShaderNodeTexVoronoi')
    vor.feature='DISTANCE_TO_EDGE';vor.inputs['Scale'].default_value=7
    nt.links.new(tc.outputs['UV'],vor.inputs['Vector'])
    ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.008
    ramp.color_ramp.elements[0].color=(.025,.035,.037,1)
    ramp.color_ramp.elements[1].position=.025;ramp.color_ramp.elements[1].color=(.075,.125,.145,1)
    nt.links.new(vor.outputs['Distance'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],nt.nodes.get('Principled BSDF').inputs['Base Color'])

    def frame(origin, tangent, normal):
        return Vector(origin), Vector(tangent).normalized(), Vector(normal).normalized()

    def point(f,u,z,d=0):
        o,t,n=f
        return o+t*u+n*d+Vector((0,0,z))

    def solid(name, shape, f, d0, d1, collection='DETAIL', material=trim, keys=()):
        count=len(shape)
        verts=[tuple(point(f,u,z,d)) for d in (d0,d1) for u,z in shape]
        faces=[tuple(reversed(range(count))),tuple(range(count,count*2))]
        faces += [(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
        return mesh(name,verts,faces,collection,material,keys or architectural_keys)

    def rect(name,f,u0,u1,z0,z1,d0,d1,material=trim,collection='DETAIL',keys=()):
        return solid(name,[(u0,z0),(u1,z0),(u1,z1),(u0,z1)],f,d0,d1,collection,material,keys)

    def tube(name, coords, radius, material=trim, collection='TRACERY', closed=False, keys=()):
        data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.resolution_u=1
        data.bevel_depth=radius;data.bevel_resolution=1;data.use_fill_caps=True
        spl=data.splines.new('POLY');spl.points.add(len(coords)-1)
        for p,co in zip(spl.points,coords):p.co=(*co,1)
        spl.use_cyclic_u=closed
        obj=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(obj)
        g['tag'](obj,collection,material,keys or architectural_keys)
        return obj

    def arch(width,sill,spring,steps=20):
        a=width/2
        # Two circles, centres at opposite spring corners, form an equilateral arch.
        left=[(-a+width*(1-math.cos(i*math.pi/3/steps)),spring+width*math.sin(i*math.pi/3/steps)) for i in range(steps+1)]
        right=[(-u,z) for u,z in reversed(left[:-1])]
        return [(-a,sill)]+left+right+[(a,sill)]

    def outline_band(name,inner,outer,f,d0,d1,material=trim):
        count=len(inner); verts=[]
        for d in (d0,d1):
            for outline in (inner,outer):verts.extend(tuple(point(f,u,z,d)) for u,z in outline)
        faces=[]
        for i in range(count):
            j=(i+1)%count
            faces.extend([(i,j,count+j,count+i),
                          (2*count+i,3*count+i,3*count+j,2*count+j),
                          (i,2*count+i,2*count+j,j),
                          (count+i,count+j,3*count+j,3*count+i)])
        return mesh(name,verts,faces,'OPENINGS',material,architectural_keys)

    def circle(name,f,u,z,r,d,profile,material=trim,petals=0):
        coords=[]
        for i in range(64):
            theta=2*math.pi*i/64;rr=r*(1+.24*math.cos(petals*theta)) if petals else r
            coords.append(tuple(point(f,u+rr*math.cos(theta),z+rr*math.sin(theta),d)))
        tube(name,coords,profile,material,closed=True)

    def window(name,host,f,width,sill,spring,style='rose',lights=2):
        recess=P['window_recess'];border=P['window_border'];profile=P['window_moulding_radius']
        if style=='door':border*=.65
        shape=arch(width,sill,spring)
        cutter=solid(name+'_CUT',shape,f,-recess,.10,'REFERENCE',dark)
        cutters[host].append(cutter)
        outline_band(name+'_dressed_surround',shape,arch(width+2*border,max(0,sill-border),spring),f,-.10,.08)
        glass_shape=arch(width-.05,sill+.025,spring)
        glazing=dark if style=='belfry' else wood if style=='door' else glass
        solid(name+'_glazing',glass_shape,f,-recess+.025,-recess+.025+P['window_glass_thickness'],'OPENINGS',glazing)
        for depth in (-.06,-.22):
            tube(name+'_archivolt', [tuple(point(f,u,z,depth)) for u,z in shape[1:-1]],profile)
        rect(name+'_sill',f,-width/2-border,width/2+border,max(0,sill-border),sill,-.08,.22)
        r=P['window_mullion_radius'];d=-recess+.12
        apex=spring+math.sqrt(3)*width/2
        if style=='rose':
            rose_r=width*P['window_rose_radius_factor']
            rose_z=apex-width*P['window_rose_drop_factor']
            if lights==2:
                circle(name+'_rose',f,0,rose_z,rose_r,d,r)
                lancet_spring=rose_z-rose_r-width*P['window_lancet_spring_factor']
                small_width=width/2-2*r
                for offset in (-width/4,width/4):
                    pts=arch(small_width,sill,lancet_spring)[1:-1]
                    tube(name+'_lancet_arch',[tuple(point(f,u+offset,z,d)) for u,z in pts],r)
                tube(name+'_mullion',[tuple(point(f,0,sill,d)),tuple(point(f,0,lancet_spring+math.sqrt(3)*small_width/2,d))],r)
            else:
                # Four western lancets grouped under two subarches, with small
                # rosettes; the first pass's giant single rose was unsupported.
                lower_spring=spring-width*.10
                for i in range(lights):
                    centre=-width/2+width*(i+.5)/lights
                    pts=arch(width/lights-.16,sill,lower_spring)[1:-1]
                    tube(name+'_four_lancet',[tuple(point(f,u+centre,z,d)) for u,z in pts],r)
                for i in range(1,lights):
                    u=-width/2+width*i/lights
                    tube(name+'_mullion',[tuple(point(f,u,sill,d)),tuple(point(f,u,lower_spring+width*.22,d))],r)
                for centre in (-width/4,width/4):
                    pts=arch(width/2-.15,sill,spring+.5)[1:-1]
                    tube(name+'_paired_subarch',[tuple(point(f,u+centre,z,d)) for u,z in pts],r)
                    circle(name+'_paired_rosette',f,centre,spring+width*.23,width*.10,d,r,petals=4)
                circle(name+'_head_rosette',f,0,apex-width*.24,width*.11,d,r,petals=4)
        elif style=='quatrefoil':
            rose_r=width*.29;rose_z=apex-width*.48
            circle(name+'_quatrefoil',f,0,rose_z,rose_r,d,r,petals=4)
            small_spring=rose_z-rose_r-width*.28
            for offset in (-width/4,width/4):
                pts=arch(width/2-.14,sill,small_spring)[1:-1]
                tube(name+'_quatrefoil_lancet',[tuple(point(f,u+offset,z,d)) for u,z in pts],r)
            tube(name+'_mullion',[tuple(point(f,0,sill,d)),tuple(point(f,0,small_spring+width*.40,d))],r)
        elif style!='door':
            tube(name+'_central_mullion',[tuple(point(f,0,sill,d)),tuple(point(f,0,apex-width*.35,d))],r)
            circle(name+'_small_rose',f,0,apex-width*.37,width*.19,d,r)
        # Visible iron bars, not a black texture painted over a wall.
        height=spring-sill
        for i in range(1,0 if style=='door' else int(height/P['window_iron_spacing'])+1):
            z=sill+i*P['window_iron_spacing']
            tube(name+'_iron_crossbar',[tuple(point(f,-width/2+.08,z,d-.03)),tuple(point(f,width/2-.08,z,d-.03))],P['window_iron_radius'],iron)
        windows.append({'name':name,'host':host,'style':style,'width':width,'sill':sill,'spring':spring,'recess':recess})

    def ledge(name,f,length,z,depth=None,height=None,material=trim):
        depth=P['cornice_depth'] if depth is None else depth
        height=P['cornice_height'] if height is None else height
        rect(name,f,-length/2,length/2,z,z+height,-.05,depth,material)
        rect(name+'_profile',f,-length/2,length/2,z+height,z+height*1.4,-.05,depth*.72,material)

    def buttress(name,f,top=None,depth=None):
        top=P['buttress_top'] if top is None else top
        depth=P['buttress_depth'] if depth is None else depth
        w=P['buttress_width'];first=P['buttress_first_step'];mid=min(P['buttress_second_step'],top*.56)
        tiers=[(0,first,w*P['buttress_base_width_factor'],depth),
               (first,mid,w,depth*P['buttress_middle_depth_factor']),
               (mid,top,w*.85,depth*P['buttress_upper_depth_factor'])]
        for i,(z0,z1,width,dep) in enumerate(tiers):
            drop=P['buttress_weathering_drop']
            rect(name+f'_stage_{i}',f,-width/2,width/2,max(0,z0-drop),z1-drop,-.10,dep,stone,'BUTTRESSES')
            # A closed wedge; rear is higher so rain drains outwards.
            verts=[tuple(point(f,u,z,d)) for u,z,d in [(-width/2,z1-drop,0),(width/2,z1-drop,0),
                   (-width/2,z1,0),(width/2,z1,0),(-width/2,z1-drop,dep+.08),(width/2,z1-drop,dep+.08)]]
            mesh(name+f'_weathering_{i}',verts,[(0,1,3,2),(0,4,5,1),(2,3,5,4),(0,2,4),(1,5,3)],'BUTTRESSES',trim,architectural_keys)
            ledge(name+f'_setback_ledge_{i}',f,width+.12,z1-drop,.12+dep,P['cornice_height']*.55)
        gargoyle(name,f,top)

    def gargoyle(name,f,z):
        # Drain silhouette follows photographs; individual beasts are not invented.
        length=P['gargoyle_length'];w=P['gargoyle_width'];h=P['gargoyle_height']
        rect(name+'_drain_spout',f,-w/2,w/2,z,z+h,.1,length,lead)
        rect(name+'_stone_drain_head',f,-w,w,z-h,z,.1,.55,trim)

    def facade_band(name,f,length,eave,mid=None,plinth=True):
        if plinth:ledge(name+'_plinth',f,length,P['plinth_height'],P['plinth_depth'])
        ledge(name+'_mid',f,length,P['cornice_mid_height'] if mid is None else mid)
        ledge(name+'_eave',f,length,eave-.38,P['cornice_eave_depth'])

    def two_rows(name,host,f,width=None):
        width=P['window_width'] if width is None else width
        window(name+'_lower',host,f,width,P['window_lower_sill'],P['window_lower_spring'])
        window(name+'_upper',host,f,width,P['window_upper_sill'],P['window_upper_spring'])

    # Five regular bays per side follow the accepted roof rhythm and P02.
    h,cap,eave=g['h'],g['cap'],g['eave'];hall=g['hall_half'];nw=g['nave_west']
    count=int(P['side_roof_count']);bay=(-h-nw)/count
    for side in (-1,1):
        f=frame((0,side*hall,0),(1,0,0),(0,side,0))
        face=frame(((nw-h)/2,side*hall,0),(1,0,0),(0,side,0))
        facade_band(f'Hall_{side}',face,-h-nw,eave,plinth=False)
        gap_width=P['side_door_width']/2+P['window_border']
        door_x=[nw+(i+.5)*bay for i in (0,count-1)]
        sections=[(nw,door_x[0]-gap_width),(door_x[0]+gap_width,door_x[1]-gap_width),
                  (door_x[1]+gap_width,-h)]
        for a,b in sections:
            pf=frame(((a+b)/2,side*hall,0),(1,0,0),(0,side,0))
            ledge(f'Hall_{side}_plinth_beside_doors',pf,b-a,P['plinth_height'],P['plinth_depth'])
        for i in range(count):
            x=nw+(i+.5)*bay
            wf=frame((x,side*hall,0),(1,0,0),(0,side,0))
            two_rows(f'Window_Hall_{side}_{i}','Hall_exterior',wf)
        for i in range(count+1):
            bf=frame((nw+i*bay,side*hall,0),(1,0,0),(0,side,0))
            buttress(f'Buttress_Hall_{side}_{i}',bf)
        # Modern evidence shows small doors below windows near each hall end.
        for index in (0,count-1):
            x=nw+(index+.5)*bay
            df=frame((x,side*hall,0),(1,0,0),(0,side,0))
            window(f'Side_portal_{side}_{index}','Hall_exterior',df,P['side_door_width'],.08,P['side_door_top']-math.sqrt(3)*P['side_door_width']/2,'door')

    # Every cap face has two rows, divided by the characteristic stepped supports.
    arc=g['local_cap']
    for direction in ('E','N','S'):
        xy=g['xy'];host='Conch_'+direction
        points=[Vector((*xy(u,v,direction),0)) for u,v in arc]
        for i,(a,b) in enumerate(zip(points,points[1:])):
            tangent=(b-a).normalized();normal=Vector((tangent.y,-tangent.x,0))
            wf=frame((a+b)/2,tangent,normal)
            two_rows(f'Window_{host}_cap_{i}',host,wf,P['conch_window_width'])
            facade_band(f'{host}_cap_band_{i}',wf,(b-a).length,eave)
        for i,p in enumerate(points):
            # Radial outward normal is the support axis at a polygon corner.
            centre=Vector((*xy(cap,0,direction),0));normal=(p-centre).normalized()
            tangent=Vector((-normal.y,normal.x,0))
            buttress(f'Buttress_{host}_cap_{i}',frame(p,tangent,normal))
        # East-facing sides of N/S arms and south-facing east-arm side: two bays.
        for sign in (-1,1):
            begin=h if (direction=='E' or sign==-1) else hall
            if direction in ('N','S'):
                begin=h if sign==-1 else hall
            # local v=-h becomes east side for N, west side for S.
            if direction=='S': begin=h if sign==1 else hall
            end=cap;segments=2 if end-begin>6 else 1
            a=Vector((*xy(begin,sign*h,direction),0));b=Vector((*xy(end,sign*h,direction),0))
            tangent=(b-a).normalized();normal=Vector((*xy(0,sign,direction),0))
            centre=(a+b)/2;length=(b-a).length
            facade_band(f'{host}_straight_{sign}',frame(centre,tangent,normal),length,eave)
            for i in range(segments):
                pos=a+(b-a)*(i+.5)/segments
                wf=frame(pos,tangent,normal)
                width=min(P['window_width'],length/segments-.8)
                two_rows(f'Window_{host}_side_{sign}_{i}',host,wf,width)
            for i in range(segments):
                pos=a+(b-a)*i/segments
                buttress(f'Buttress_{host}_side_{sign}_{i}',frame(pos,tangent,normal))

    # Sacristy: two stages with quatrefoils and a complete lower roof, M15–M17.
    sx0,sx1,sy0,sy1=g['sx0'],g['sx1'],g['sy0'],g['sy1']
    annex_faces=[((sx1,(sy0+sy1)/2,0),(0,1,0),(1,0,0),sy1-sy0),
                 (((sx0+sx1)/2,sy1,0),(1,0,0),(0,1,0),sx1-sx0)]
    for i,(origin,t,n,length) in enumerate(annex_faces):
        f=frame(origin,t,n);facade_band(f'Sacristy_{i}',f,length,P['sacristy_eave'],P['sacristy_mid_band'])
        for j in range(2):
            wf=frame(point(f,(j-.5)*length/2,0),t,n)
            for label,sill,spring in [('lower',P['sacristy_lower_sill'],P['sacristy_lower_spring']),
                                     ('upper',P['sacristy_upper_sill'],P['sacristy_upper_spring'])]:
                window(f'Window_Sacristy_{i}_{j}_{label}','Sacristy_NE',wf,P['sacristy_window_width'],sill,spring,'quatrefoil')
        for j in range(3):
            bf=frame(point(f,-length/2+j*length/2,0),t,n)
            buttress(f'Buttress_Sacristy_{i}_{j}',bf,P['sacristy_buttress_top'],P['sacristy_buttress_depth'])

    def railing(name,f,length,z):
        height=P['balustrade_height'];radius=P['balustrade_bar_radius'];pitch=P['balustrade_pitch']
        for elevation in (z,z+height):
            tube(name+'_rail',[tuple(point(f,-length/2,elevation,.20)),tuple(point(f,length/2,elevation,.20))],radius,trim,'DETAIL')
        number=max(1,round(length/pitch));cell=length/number
        for i in range(number):
            u=-length/2+(i+.5)*cell
            tube(name+'_diamond',[tuple(point(f,u-cell/2,z+height/2,.20)),tuple(point(f,u,z+height,.20)),
                                  tuple(point(f,u+cell/2,z+height/2,.20)),tuple(point(f,u,z,.20))],radius,trim,'DETAIL',True)
            circle(name+'_quatrefoil',f,u,z+height/2,cell*.22,.20,radius*.65,trim,petals=4)

    # Tower galleries, pointed belfries and gabled octagonal upper stages.
    tx,td,tw=g['tx'],g['td'],g['tw']
    for side in (-1,1):
        ty=side*P['west_tower_center_y'];suffix='S' if side<0 else 'N'
        host='Tower_shaft_'+suffix
        faces=[((tx-td,ty,0),(0,1,0),(-1,0,0),2*tw),
               ((tx+td,ty,0),(0,1,0),(1,0,0),2*tw),
               ((tx,ty-tw,0),(1,0,0),(0,-1,0),2*td),
               ((tx,ty+tw,0),(1,0,0),(0,1,0),2*td)]
        for index,(o,t,n,length) in enumerate(faces):
            f=frame(o,t,n)
            window(f'Window_Tower_{suffix}_{index}_lower',host,f,P['tower_window_width'],P['tower_lower_sill'],P['tower_lower_spring'])
            window(f'Window_Tower_{suffix}_{index}_belfry',host,f,P['tower_window_width'],P['tower_belfry_sill'],P['tower_belfry_spring'],'belfry')
            for z in (P['plinth_height'],P['tower_gallery_lower'],P['tower_gallery_top']):
                ledge(f'Tower_{suffix}_{index}_gallery_{z}',f,length+.25,z,P['tower_gallery_depth'],P['tower_gallery_height'])
            railing(f'Tower_{suffix}_{index}_parapet',f,length,P['tower_gallery_top']+.35)
        # Ledges must wrap projecting corner supports as well as the core face.
        # Otherwise they disappear behind the coarse support blocks in SW.
        bands=[(P['tower_support_belt_low'],1),(P['tower_support_belt_middle'],1),
               (P['corner_support_first_step'],1),
               (P['corner_support_second_step'],P['corner_support_mid_factor']),
               (P['west_tower_shoulder'],P['corner_support_top_factor'])]
        for z,factor in bands:
            for xsign in (-1,1):
                for ysign in (-1,1):
                    pieces=[]
                    for along in ('X','Y'):
                        width=P['corner_support_width'];depth=P['corner_support_depth']
                        cx=tx+xsign*(td+depth*factor/2-width/2) if along=='X' else tx+xsign*(td-width/2)
                        cy=ty+ysign*(tw-width/2) if along=='X' else ty+ysign*(tw+depth*factor/2-width/2)
                        dx,dy=(depth*factor+width,width) if along=='X' else (width,depth*factor+width)
                        projection=P['tower_gallery_depth']/2
                        pieces.append(box('Tower_support_profiled_ledge',cx-dx/2-projection,cx+dx/2+projection,
                            cy-dy/2-projection,cy+dy/2+projection,z-.12,z+.12,'DETAIL',trim,architectural_keys))
                    # Crossed ledge pieces share cap planes; union to avoid
                    # coincident faces producing black notches in upward views.
                    bpy.context.view_layer.objects.active=pieces[0]
                    mod=pieces[0].modifiers.new('Union_corner_ledge','BOOLEAN')
                    mod.operation='UNION';mod.solver='EXACT';mod.object=pieces[1]
                    bpy.ops.object.modifier_apply(modifier=mod.name)
                    bpy.data.objects.remove(pieces[1],do_unlink=True)
        pts=[Vector((x,y,0)) for x,y in ring(tx,ty,P['west_tower_octagon_radius'])]
        for index,(a,b) in enumerate(zip(pts,pts[1:]+pts[:1])):
            t=(b-a).normalized();n=Vector((t.y,-t.x,0));f=frame((a+b)/2,t,n);length=(b-a).length
            window(f'Window_Upper_{suffix}_{index}','Tower_upper_octagon_'+suffix,f,
                   P['tower_upper_window_width'],P['tower_upper_sill'],P['tower_upper_spring'],'belfry')
            # Thin gable cap around the helm base, with raised moulded edges.
            gable_base=max(P['tower_gable_base'],P['tower_upper_spring']+math.sqrt(3)*P['tower_upper_window_width']/2+.10)
            shape=[(-length/2,gable_base),(length/2,gable_base),
                   (0,P['tower_gable_top'])]
            solid(f'Tower_gable_{suffix}_{index}',shape,f,-P['tower_gable_depth'],.04,'TOWERS',stone)
            tube(f'Tower_gable_edge_{suffix}_{index}',[tuple(point(f,u,z,.12)) for u,z in shape[1:]+shape[:1]],P['window_moulding_radius'],trim,'DETAIL')
            circle(f'Tower_gable_oculus_{suffix}_{index}',f,0,P['tower_gable_base']+P['oculus_height_above_base'],P['oculus_radius'],.10,P['window_mullion_radius'])

    # Replace the coarse blank west triangle by flat crest and a traceried clock gable.
    bpy.data.objects.remove(bpy.data.objects['West_central_gable'],do_unlink=True)
    front=g['front']-P['west_front_depth'];gap=g['half_gap']
    west=frame((front,0,0),(0,1,0),(-1,0,0))
    host='West_hall_bridge'
    rect('West_upper_connecting_facade',west,-gap,gap,eave,P['west_central_eave'],-P['west_front_depth'],0,stone,'MASSING')
    ledge('West_middle_cornice',west,2*gap,P['west_facade_base_top'])
    ledge('West_eave_cornice',west,2*gap,P['west_central_eave']-.38,P['cornice_eave_depth'])
    for sign in (-1,1):
        f=frame(point(west,sign*(gap+P['portal_width']/2)/2,0),west[1],west[2])
        ledge('West_plinth_beside_portal',f,gap-P['portal_width']/2,P['plinth_height'],P['plinth_depth'])
    window('West_main_four_light',host,west,P['west_main_window_width'],P['west_main_window_sill'],P['west_main_window_spring'],'rose',4)
    window('West_portal',host,west,P['portal_width'],P['portal_sill'],P['portal_spring'],'belfry')
    # Red double doors and carved tympanum within the deeply moulded portal.
    d=-P['window_recess']+.09;w=P['portal_width'];sill=P['portal_sill'];spring=P['portal_spring']
    rect('West_red_double_doors',west,-w/2+.12,w/2-.12,sill,P['portal_door_top'],d,d+.04,wood,'OPENINGS')
    rect('West_trumeau',west,-P['portal_trumeau_width']/2,P['portal_trumeau_width']/2,sill,spring,d-.02,.10,trim)
    for i in range(int(P['portal_moulding_count'])):
        shape=arch(w+2*i*P['portal_moulding_pitch'],sill,spring)
        tube('Portal_nested_archivolt',[tuple(point(west,u,z,.10+i*.035)) for u,z in shape[1:-1]],P['window_moulding_radius'],trim,'DETAIL')
    shape=arch(w-.18,P['portal_door_top'],spring)
    solid('Portal_carved_tympanum',shape,west,d-.02,d+.08,'DETAIL',relief)
    # Abstract low relief foliage rows, avoiding unsupported exact sculptural claims.
    apex=spring+math.sqrt(3)*w/2
    for row in range(8):
        z=P['portal_door_top']+.18+row*P['portal_foliage_row_pitch']
        if z>apex-.25:continue
        available=max(.10,w/2-(z-spring)*.50)
        for column in range(-5,6):
            u=column*P['portal_foliage_pitch']+(row%2)*P['portal_foliage_pitch']/2
            if abs(u)>available-.12:continue
            lr=P['portal_foliage_radius']
            leaf=[(u-lr,z),(u,z+lr*1.6),(u+lr,z),(u,z-lr*.8)]
            solid('Portal_foliage_relief',leaf,west,d+.08,d+.08+P['portal_relief_depth'],'DETAIL',relief)
    # Central figure reduced to a robe silhouette and head, as M13 allows.
    fig_h=P['portal_figure_height'];fig_z=P['portal_door_top']+.12
    solid('Portal_figure_robe',[(-.20,fig_z),(.20,fig_z),(.10,fig_z+fig_h*.78),(-.10,fig_z+fig_h*.78)],west,d+.18,d+.36,'DETAIL',trim)
    circle('Portal_figure_head',west,0,fig_z+fig_h*.90,fig_h*.10,d+.35,.08,trim)
    for offset in (-w/4,w/4):
        for row in range(5):
            z=.7+row*.85
            tube('Door_iron_scroll',[tuple(point(west,offset-.45,z,d+.07)),tuple(point(west,offset,z+.20,d+.07)),tuple(point(west,offset+.45,z,d+.07))],P['portal_iron_scroll_radius'],iron,'DETAIL')
    ledge('West_gallery',west,2*gap,P['west_central_eave'],P['tower_gallery_depth'],P['tower_gallery_height'])
    railing('West_open_parapet',west,2*gap,P['west_central_eave']+.35)
    clock_w=P['west_clock_window_width']+2*P['window_border']
    clock_shape=[(-clock_w/2,P['west_central_eave']),(clock_w/2,P['west_central_eave']),
                 (clock_w/2,P['west_clock_spring']),(0,P['west_clock_gable_top']),(-clock_w/2,P['west_clock_spring'])]
    solid('West_clock_gable',clock_shape,west,-P['west_front_depth'],.12,'TOWERS',stone)
    clock_frame=frame(point(west,0,0,.12),west[1],west[2])
    window('West_clock_glazing','West_clock_gable',clock_frame,P['west_clock_window_width'],P['west_clock_sill'],P['west_clock_spring'],'rose')
    tube('West_clock_gable_moulding',[tuple(point(west,u,z,.24)) for u,z in clock_shape[2:]],P['window_moulding_radius'],trim,'DETAIL')
    clock_z=(P['west_clock_sill']+P['west_clock_spring'])/2
    circle('West_clock_open_dial',west,0,clock_z,P['west_clock_radius'],.27,.035,lead)
    for i in range(12):
        theta=2*math.pi*i/12;r=P['west_clock_radius']
        tube('Clock_hour_mark',[tuple(point(west,r*.84*math.sin(theta),clock_z+r*.84*math.cos(theta),.29)),
                                tuple(point(west,r*math.sin(theta),clock_z+r*math.cos(theta),.29))],.035,lead,'DETAIL')
    tube('Clock_hands',[tuple(point(west,-.35,clock_z+.75,.30)),tuple(point(west,0,clock_z,.30)),tuple(point(west,.55,clock_z-.2,.30))],.04,lead,'DETAIL')

    def knob(name,position,radius):
        # Compact leaf/finial silhouette, explicitly simplified from M14.
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=radius,location=position)
        obj=bpy.context.object;obj.name=name
        g['tag'](obj,'DETAIL',trim,('crocket_radius','crocket_pitch'))
        return obj

    # Clock crest: pinnacles, small blind gables and sculpted edge rhythm, M14.
    for sign in (-1,1):
        u=sign*(clock_w/2+.18);width=P['crest_pinnacle_width'];z0=P['west_central_eave']
        z1=P['west_clock_gable_top']-.8
        rect('Clock_flanking_pinnacle',west,u-width/2,u+width/2,z0,z1,-.20,.30,stone)
        solid('Clock_flanking_pinnacle_tip',[(u-width,z1),(u+width,z1),(u,z1+P['crest_pinnacle_rise'])],west,-.20,.30,'DETAIL',trim)
        for z in range(int(P['west_clock_spring']),int(z1+P['crest_pinnacle_rise'])):
            knob('Pinnacle_crocket',point(west,u+sign*width*.9,z,.32),P['crocket_radius'])
        u=sign*(clock_w/2+P['crest_side_gable_width']/2+.25)
        sw=P['crest_side_gable_width'];sz=P['crest_side_gable_sill'];st=sz+P['crest_side_gable_height']
        shape=[(u-sw/2,sz),(u+sw/2,sz),(u,st)]
        solid('Clock_side_blind_gable',shape,west,-.12,.22,'DETAIL',stone)
        tube('Clock_side_gable_edge',[tuple(point(west,x,z,.3)) for x,z in shape[1:]+shape[:1]],P['window_moulding_radius'],trim,'DETAIL')
        circle('Clock_side_blind_quatrefoil',west,u,sz+sw*.6,sw*.23,.3,P['balustrade_bar_radius'],trim,petals=4)
    for a,b in [(clock_shape[2],clock_shape[3]),(clock_shape[3],clock_shape[4])]:
        delta=Vector((b[0]-a[0],b[1]-a[1]));steps=max(1,int(delta.length/P['crocket_pitch']))
        for i in range(steps+1):
            u,z=Vector(a)+delta*i/steps
            knob('Clock_gable_crocket',point(west,u,z,.32),P['crocket_radius'])

    # The main nave roof begins behind the tower shafts, not at the west facade.
    # A low bridge roof completes the inter-tower volume behind its gallery crest.
    main_roof=bpy.data.objects['Nave_main_roof']
    for vertex in main_roof.data.vertices:
        if vertex.co.x<g['nave_west']:vertex.co.x=g['nave_west']
    box('West_bridge_low_roof',g['front'],g['nave_west'],-gap,gap,eave,eave+P['cornice_height'],'ROOFS',slate,('nave_west_end','wall_eave_height','cornice_height','west_tower_center_x','west_tower_core_depth','west_tower_center_y','west_tower_core_width'))
    # Close the rider/roof junction by embedding its foot into the sloped roof.
    rider=bpy.data.objects['Crossing_rider_base']
    for vertex in rider.data.vertices:
        if abs(vertex.co.z-g['ridge'])<.01:vertex.co.z-=P['rider_embed_depth']
    rider['parameter_keys']+=', rider_embed_depth'
    # Reentrant stair cap and narrow lighting slits; mostly hidden in modern views.
    cx,cy=P['north_stair_center_x'],P['north_stair_center_y'];rr=P['north_stair_radius'];zt=P['north_stair_top']
    taper('Stair_slate_cap',cx,cy,rr+.08,0,zt,zt+P['stair_roof_rise'],'ROOFS',slate,('north_stair_center_x','north_stair_center_y','north_stair_radius','north_stair_top','stair_roof_rise'))
    for z in range(5,int(zt),int(P['stair_slit_spacing'])):
        sf=frame((cx,cy+rr,0),(1,0,0),(0,1,0));width=P['stair_slit_width']
        rect('Stair_light_slit',sf,-width/2,width/2,z,z+P['stair_slit_height'],0,.025,dark,'OPENINGS')

    # Batch each wall's disjoint cutters into one exact boolean operation.
    for host,objs in cutters.items():
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objs:obj.select_set(True)
        bpy.context.view_layer.objects.active=objs[0]
        if len(objs)>1:bpy.ops.object.join()
        cut=objs[0]
        target=bpy.data.objects[host];bpy.context.view_layer.objects.active=target
        modifier=target.modifiers.new('Actual_blind_window_recesses','BOOLEAN')
        modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cut
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.data.objects.remove(cut,do_unlink=True)
        target['recess_depth_m']=P['window_recess'];target['opening_count']=len(objs)

    # Roof seams follow actual mesh edges; no invented texture dimensions.
    for obj in list(bpy.data.collections['ROOFS'].objects):
        if obj.type!='MESH' or 'roof' not in obj.name.lower():continue
        for edge in obj.data.edges:
            a,b=[obj.matrix_world @ obj.data.vertices[v].co for v in edge.vertices]
            if min(a.z,b.z)<eave-.10 or abs(a.z-b.z)<.01 and a.z<eave+.5:continue
            tube('Lead_seam_'+obj.name,[tuple(a+Vector((0,0,.025))),tuple(b+Vector((0,0,.025)))],P['roof_edge_radius'],lead,'DETAIL')
    # Dormers on visible conch roof facets, M18; annex roof vent from M17.
    def dormer(name,f,z):
        w=P['roof_dormer_width'];height=P['roof_dormer_height'];depth=P['roof_dormer_depth']
        rect(name+'_vent_box',f,-w/2,w/2,z-P['roof_dormer_embed_depth'],z+height,0,depth,lead)
        rect(name+'_dark_grille',f,-w*.36,w*.36,z+.1,z+height*.78,depth+.005,depth+.02,dark)
        shape=[(-w*.65,z+height*.85),(w*.65,z+height*.85),(0,z+height*1.2)]
        solid(name+'_hood',shape,f,-.05,depth+.1,'DETAIL',slate)
        for j in range(6):
            u=(j-2.5)*w*.12
            tube(name+'_vent_bar',[tuple(point(f,u,z+.1,depth+.04)),tuple(point(f,u,z+height*.78,depth+.04))],P['window_iron_radius'],iron,'DETAIL')
    for direction in ('E','N','S'):
        u=cap+h*.65;v=0;xx,yy=g['xy'](u,v,direction)
        nx,ny=g['xy'](1,0,direction);t=(-ny,nx,0)
        # Approximate front hip plane height from the same roof slope.
        z=g['ridge']+(g['roof_bottom']-g['ridge'])*.65
        dormer('Roof_vent_'+direction,frame((xx,yy,0),t,(nx,ny,0)),z)
        apex=g['xy'](cap,0,direction);z=g['ridge'];radius=P['metal_rod_radius']
        f=frame((*apex,0),(1,0,0),(0,1,0));ch=P['metal_cross_height'];cw=P['metal_cross_width']
        tube('Conch_cross_'+direction,[tuple(point(f,0,z)),tuple(point(f,0,z+ch))],radius,lead,'DETAIL')
        tube('Conch_crossbar_'+direction,[tuple(point(f,-cw/2,z+ch*.65)),tuple(point(f,cw/2,z+ch*.65))],radius,lead,'DETAIL')
    centre_x=(sx0+sx1)/2;centre_y=(sy0+sy1)/2
    dormer('Sacristy_roof_vent',frame((sx1-2.5,centre_y,0),(0,1,0),(1,0,0)),P['sacristy_dormer_level'])
    # Lantern cornices and a modern metal terminal on the roof rider.
    rr=P['roof_rider_radius']
    for z in (P['roof_rider_body_top'],P['roof_rider_lantern_top']):
        coords=[(x,y,z) for x,y in ring(0,0,rr+P['roof_rider_trim'])]
        tube('Rider_lantern_cornice',coords,P['roof_edge_radius']*2,lead,'DETAIL',True)
    tube('Rider_terminal',[ (0,0,P['roof_rider_top']),(0,0,P['roof_rider_top']+P['metal_cross_height'])],P['metal_rod_radius'],lead,'DETAIL')

    # Every mesh gets metre-scale UVs. Vertical face U is its own horizontal
    # tangent; V is world height. Sloped roof V follows the roof plane uphill.
    for obj in bpy.data.objects:
        if obj.type!='MESH' or not obj.users_collection or obj.users_collection[0].name=='REFERENCE':continue
        uv=obj.data.uv_layers.new(name='Metre_face_projection')
        for face in obj.data.polygons:
            normal=face.normal
            horizontal=Vector((-normal.y,normal.x,0))
            if horizontal.length<.01:horizontal=Vector((1,0,0))
            horizontal.normalize()
            vertical=normal.cross(horizontal).normalized()
            if vertical.z<0:vertical=-vertical
            for loop_index in face.loop_indices:
                pos=obj.matrix_world @ obj.data.vertices[obj.data.loops[loop_index].vertex_index].co
                uv.data[loop_index].uv=(pos.dot(horizontal),pos.dot(vertical))
        if obj.name.startswith('Tower_stone_helm'):
            obj.data.materials.clear();obj.data.materials.append(stone)
        if obj.users_collection[0].name!='REFERENCE':
            obj['quality_stage']='developed exterior, approximate photo-based detail'
    import json
    report=g['ROOT']/'validation/reports/goal-2-architecture.json'
    report.write_text(json.dumps({'iteration':g['ITERATION'],'windows':windows,
                      'window_count':len(windows),'material_names':[m.name for m in bpy.data.materials],
                      'camera_changes':False},indent=2)+'\n',encoding='utf-8')
    print('ARCHITECTURE BUILT',len(windows),'recessed exterior openings')
