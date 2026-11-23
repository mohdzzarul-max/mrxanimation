"""Core Blender helpers: scene setup, materials, primitives, rigging, keyframes."""
import math, os
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEX = os.path.join(ROOT, "textures")
os.makedirs(TEX, exist_ok=True)
FPS = 30


# ---------------------------------------------------------------- scene
def new_scene(res=(540, 960), samples=20):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.04
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.cycles.denoising_prefilter = "FAST"
    sc.cycles.denoising_quality = "FAST"
    sc.cycles.max_bounces = 5
    sc.cycles.diffuse_bounces = 2
    sc.cycles.glossy_bounces = 2
    sc.cycles.transmission_bounces = 4
    sc.cycles.transparent_max_bounces = 8
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.cycles.blur_glossy = 1.0
    sc.render.use_persistent_data = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.fps = FPS
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_depth = "8"
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Punchy"
    except TypeError:
        pass
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = 0.45
    w = bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    world_color((0.02, 0.02, 0.03), 1.0)
    return sc


def world_color(c, strength=1.0):
    bg = bpy.context.scene.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (*c, 1)
    bg.inputs[1].default_value = strength


# ---------------------------------------------------------------- materials
_MATS = {}


def mat(name, color=(0.5, 0.5, 0.5), rough=0.5, metal=0.0, coat=0.0, emit=None, emit_str=0.0,
        sss=0.0, spec=0.5, bump=0.0, bump_scale=60.0, alpha_img=None, img=None, sheen=0.0):
    """Principled material. bump>0 adds fine noise bump (fabric/knit/plastic grain)."""
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Specular IOR Level"].default_value = spec
    if sheen:
        p.inputs["Sheen Weight"].default_value = sheen
        p.inputs["Sheen Tint"].default_value = (1, 1, 1, 1)
    if sss:
        p.inputs["Subsurface Weight"].default_value = sss
        p.inputs["Subsurface Radius"].default_value = (0.9, 0.35, 0.2)
        p.inputs["Subsurface Scale"].default_value = 0.02
    if emit:
        p.inputs["Emission Color"].default_value = (*emit, 1)
        p.inputs["Emission Strength"].default_value = emit_str
    if bump:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = bump_scale
        nz.inputs["Detail"].default_value = 4
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        b = nt.nodes.new("ShaderNodeBump")
        b.inputs["Strength"].default_value = bump
        b.inputs["Distance"].default_value = 0.01
        nt.links.new(nz.outputs["Fac"], b.inputs["Height"])
        nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    if img:
        it = nt.nodes.new("ShaderNodeTexImage")
        it.image = bpy.data.images.load(img, check_existing=True)
        it.extension = "CLIP"
        nt.links.new(it.outputs["Color"], p.inputs["Base Color"])
        if alpha_img:
            nt.links.new(it.outputs["Alpha"], p.inputs["Alpha"])
        if emit:
            nt.links.new(it.outputs["Color"], p.inputs["Emission Color"])
    _MATS[name] = m
    return m


def emission_mat(name, color, strength=5.0):
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs[0].default_value = (*color, 1)
    e.inputs[1].default_value = strength
    nt.links.new(e.outputs[0], out.inputs[0])
    _MATS[name] = m
    return m


def decal_mat(name, img_path, emit_strength=0.0, rough=0.5):
    """Image decal with alpha (labels, X emblems, posters)."""
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Roughness"].default_value = rough
    it = nt.nodes.new("ShaderNodeTexImage")
    it.image = bpy.data.images.load(img_path, check_existing=True)
    it.extension = "CLIP"
    nt.links.new(it.outputs["Color"], p.inputs["Base Color"])
    nt.links.new(it.outputs["Alpha"], p.inputs["Alpha"])
    if emit_strength:
        nt.links.new(it.outputs["Color"], p.inputs["Emission Color"])
        p.inputs["Emission Strength"].default_value = emit_strength
    _MATS[name] = m
    return m


def set_mat(o, m):
    o.data.materials.clear()
    o.data.materials.append(m)
    return o


# ---------------------------------------------------------------- primitives
def _post(o, name, m, smooth=True, parent=None):
    o.name = name
    if m:
        set_mat(o, m)
    if smooth and o.type == "MESH":
        for p in o.data.polygons:
            p.use_smooth = True
    if parent:
        o.parent = parent
    return o


def sphere(name, loc=(0, 0, 0), r=1.0, scale=(1, 1, 1), m=None, seg=48, rings=24, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=seg, ring_count=rings, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = scale
    return _post(o, name, m)


def cyl(name, loc=(0, 0, 0), r=1.0, depth=1.0, m=None, verts=40, rot=(0, 0, 0), scale=(1, 1, 1), bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, vertices=verts, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = scale
    if bevel:
        add_bevel(o, bevel, 3)
    _post(o, name, m)
    autosmooth(o)
    return o


def box(name, loc=(0, 0, 0), size=(1, 1, 1), m=None, bevel=0.0, seg=4, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        add_bevel(o, bevel, seg)
    _post(o, name, m)
    autosmooth(o)
    return o


def rbox(name, loc, size, m=None, round_=0.3, rot=(0, 0, 0), sub=2):
    """Soft rounded box (subdivided cube, for chibi fabric/body volumes)."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    add_bevel(o, round_ * min(size), 3)
    sm = o.modifiers.new("subd", "SUBSURF")
    sm.levels = sub
    sm.render_levels = sub
    return _post(o, name, m)


def torus(name, loc=(0, 0, 0), R=1.0, r=0.1, m=None, rot=(0, 0, 0), scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc, rotation=rot,
                                     major_segments=48, minor_segments=12)
    o = bpy.context.object
    o.scale = scale
    return _post(o, name, m)


def plane(name, loc=(0, 0, 0), size=(1, 1), m=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = (size[0], size[1], 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return _post(o, name, m, smooth=False)


def poly_prism(name, pts2d, depth, m=None, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.0):
    """Extrude a 2D outline (x,z in local plane facing -Y) into a thin prism."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    front = [bm.verts.new((x, -depth / 2, z)) for x, z in pts2d]
    back = [bm.verts.new((x, depth / 2, z)) for x, z in pts2d]
    bm.faces.new(front[::-1])
    bm.faces.new(back)
    n = len(pts2d)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((front[i], front[j], back[j], back[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = rot
    if m:
        set_mat(o, m)
    if bevel:
        add_bevel(o, bevel, 2)
    return o


def half_dome(name, r, m=None, scale=(1, 1, 1), keep_upper=True):
    """Hemisphere shell used as eyelid (rotates about local X to open/close)."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=40, ring_count=20)
    o = bpy.context.object
    bm = bmesh.new()
    bm.from_mesh(o.data)
    kill = [v for v in bm.verts if (v.co.z < -1e-4 if keep_upper else v.co.z > 1e-4)]
    bmesh.ops.delete(bm, geom=kill, context="VERTS")
    bm.to_mesh(o.data)
    bm.free()
    sol = o.modifiers.new("solid", "SOLIDIFY")
    sol.thickness = r * 0.08
    o.scale = scale
    return _post(o, name, m)


def add_bevel(o, w, seg=3):
    b = o.modifiers.new("bevel", "BEVEL")
    b.width = w
    b.segments = seg
    b.limit_method = "ANGLE"
    return b


def autosmooth(o):
    for p in o.data.polygons:
        p.use_smooth = True
    try:
        for x in bpy.context.selected_objects:
            x.select_set(False)
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
    except Exception:
        pass


def curve_tube(name, pts, radius, m=None, res=12):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 4
    cu.use_fill_caps = True
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    sp.resolution_u = res
    o = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(o)
    if m:
        o.data.materials.append(m)
    return o


def text_obj(name, body, size=0.1, m=None, loc=(0, 0, 0), rot=(math.pi / 2, 0, 0), font=None, extrude=0.0,
             align="CENTER"):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.align_x = align
    cu.align_y = "CENTER"
    if font:
        cu.font = bpy.data.fonts.load(font, check_existing=True)
    o = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = rot
    if m:
        o.data.materials.append(m)
    return o


def empty(name, loc=(0, 0, 0), parent=None):
    o = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.empty_display_size = 0.1
    if parent:
        o.parent = parent
    return o


# ---------------------------------------------------------------- rigging
def make_armature(name, bones):
    """bones: list of (name, head, tail, parent or None). Returns armature object."""
    arm = bpy.data.armatures.new(name)
    o = bpy.data.objects.new(name, arm)
    bpy.context.collection.objects.link(o)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.edit_bones
    for bn, h, t, par in bones:
        b = eb.new(bn)
        b.head = h
        b.tail = t
        if par:
            b.parent = eb[par]
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in o.pose.bones:
        pb.rotation_mode = "XYZ"
    o.show_in_front = True
    arm.display_type = "STICK"
    return o


def bind(obj, arm, bone):
    """Rigid-bind a mesh part to a bone (vinyl-toy style segmented rig)."""
    bpy.context.view_layer.update()
    mw = obj.matrix_world.copy()
    obj.parent = arm
    obj.parent_type = "BONE"
    obj.parent_bone = bone
    b = arm.data.bones[bone]
    obj.matrix_parent_inverse = (arm.matrix_world @ b.matrix_local @ Matrix.Translation((0, b.length, 0))).inverted()
    obj.matrix_world = mw
    bpy.context.view_layer.update()
    obj.matrix_world = mw


# ---------------------------------------------------------------- keyframes
def key(target, path, frame, value, index=-1, interp=None):
    """Insert a keyframe. value may be a scalar or a tuple. interp: 'BEZIER','LINEAR','CONSTANT','BACK','ELASTIC'."""
    if isinstance(value, (tuple, list)):
        setattr_path(target, path, value)
        target.keyframe_insert(path, frame=frame)
    else:
        if index >= 0:
            getattr(target, path)[index] = value
            target.keyframe_insert(path, index=index, frame=frame)
        else:
            setattr_path(target, path, value)
            target.keyframe_insert(path, frame=frame)
    if interp:
        set_interp_at(target, path, frame, interp)


def setattr_path(t, path, v):
    if "." in path or "[" in path:
        t.path_resolve(path)  # validate
        exec(f"t.{path} = v")
    else:
        cur = getattr(t, path)
        if hasattr(cur, "__len__") and not isinstance(v, (int, float)):
            for i, x in enumerate(v):
                cur[i] = x
        else:
            setattr(t, path, v)


def _fcurves_for(id_data):
    ad = id_data.animation_data
    if not ad or not ad.action:
        return []
    act = ad.action
    try:
        from bpy_extras.anim_utils import action_get_channelbag_for_slot
        cb = action_get_channelbag_for_slot(act, ad.action_slot)
        return cb.fcurves if cb else []
    except Exception:
        return getattr(act, "fcurves", [])


def set_interp_at(target, path, frame, interp):
    id_data = target.id_data
    full = target.path_from_id(path) if target != id_data else path
    for fc in _fcurves_for(id_data):
        if fc.data_path == full:
            for kp in fc.keyframe_points:
                if abs(kp.co[0] - frame) < 0.01:
                    kp.interpolation = interp
                    if interp == "BACK":
                        kp.easing = "EASE_OUT"
                    if interp == "ELASTIC":
                        kp.easing = "EASE_OUT"


def pose(arm, bone, frame, rot=None, loc=None, scale=None, interp=None):
    pb = arm.pose.bones[bone]
    if rot is not None:
        pb.rotation_euler = [math.radians(a) for a in rot]
        pb.keyframe_insert("rotation_euler", frame=frame)
        if interp:
            set_interp_at(pb, "rotation_euler", frame, interp)
    if loc is not None:
        pb.location = loc
        pb.keyframe_insert("location", frame=frame)
        if interp:
            set_interp_at(pb, "location", frame, interp)
    if scale is not None:
        pb.scale = scale if isinstance(scale, (tuple, list)) else (scale,) * 3
        pb.keyframe_insert("scale", frame=frame)
        if interp:
            set_interp_at(pb, "scale", frame, interp)


def obj_key(o, frame, loc=None, rot=None, scale=None, interp=None):
    if loc is not None:
        o.location = loc
        o.keyframe_insert("location", frame=frame)
        if interp:
            set_interp_at(o, "location", frame, interp)
    if rot is not None:
        o.rotation_euler = [math.radians(a) for a in rot]
        o.keyframe_insert("rotation_euler", frame=frame)
        if interp:
            set_interp_at(o, "rotation_euler", frame, interp)
    if scale is not None:
        o.scale = scale if isinstance(scale, (tuple, list)) else (scale,) * 3
        o.keyframe_insert("scale", frame=frame)
        if interp:
            set_interp_at(o, "scale", frame, interp)


def vis_key(o, frame, visible):
    """Keyframe render visibility (prop swaps, e.g. fist <-> pointing glove)."""
    o.hide_render = not visible
    o.hide_viewport = not visible
    o.keyframe_insert("hide_render", frame=frame)
    o.keyframe_insert("hide_viewport", frame=frame)
    for c in o.children:
        vis_key(c, frame, visible)


# ---------------------------------------------------------------- lights & camera
def area(name, loc, target=(0, 0, 0.6), energy=300, color=(1, 1, 1), size=1.0, shape="RECTANGLE", size_y=None):
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy = energy
    ld.color = color
    ld.shape = shape
    ld.size = size
    if size_y:
        ld.size_y = size_y
    o = bpy.data.objects.new(name, ld)
    bpy.context.collection.objects.link(o)
    o.location = loc
    look_at(o, target)
    return o


def point(name, loc, energy=50, color=(1, 1, 1), radius=0.05):
    ld = bpy.data.lights.new(name, "POINT")
    ld.energy = energy
    ld.color = color
    ld.shadow_soft_size = radius
    o = bpy.data.objects.new(name, ld)
    bpy.context.collection.objects.link(o)
    o.location = loc
    return o


def spot(name, loc, target, energy=500, color=(1, 1, 1), angle=30, blend=0.3, radius=0.05):
    ld = bpy.data.lights.new(name, "SPOT")
    ld.energy = energy
    ld.color = color
    ld.spot_size = math.radians(angle)
    ld.spot_blend = blend
    ld.shadow_soft_size = radius
    o = bpy.data.objects.new(name, ld)
    bpy.context.collection.objects.link(o)
    o.location = loc
    look_at(o, target)
    return o


def look_at(o, target):
    d = Vector(target) - o.location
    o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def camera(name="Cam", lens=50, focus=None, fstop=2.8):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.sensor_width = 36
    cd.sensor_fit = "VERTICAL"
    cd.sensor_height = 64
    cd.clip_start = 0.01
    o = bpy.data.objects.new(name, cd)
    bpy.context.collection.objects.link(o)
    bpy.context.scene.camera = o
    tgt = empty(name + "_target")
    tr = o.constraints.new("TRACK_TO")
    tr.target = tgt
    tr.track_axis = "TRACK_NEGATIVE_Z"
    tr.up_axis = "UP_Y"
    cd.dof.use_dof = focus is not None
    cd.dof.aperture_fstop = fstop
    foc = empty(name + "_focus")
    cd.dof.focus_object = foc
    if focus is not None:
        foc.location = focus
    return o, tgt, foc


def cam_key(cam, tgt, frame, pos, look, interp=None, lens=None, roll=None):
    obj_key(cam, frame, loc=pos, interp=interp)
    obj_key(tgt, frame, loc=look, interp=interp)
    if lens is not None:
        cam.data.lens = lens
        cam.data.keyframe_insert("lens", frame=frame)
        if interp:
            set_interp_at(cam.data, "lens", frame, interp)


def deg(*a):
    return tuple(math.radians(x) for x in a)
