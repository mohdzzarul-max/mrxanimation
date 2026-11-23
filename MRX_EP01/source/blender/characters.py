"""The three rigged characters, built to the turnaround sheets in references/.

Convention: Z up, characters face -Y at rest, ground at z=0. Character's left = +X.
Each builder returns a Character with .arm (armature), .root and facial controls.
Body parts are rigidly bound to bones (vinyl-toy segmented rig); faces use
object-level controls (eyelids, gaze pivots, brows, mouth, moustache).
"""
import math, os
import bpy
from mathutils import Vector, Matrix
from lib import (mat, emission_mat, decal_mat, sphere, cyl, box, rbox, torus, plane, poly_prism, half_dome,
                 make_armature, bind, empty, pose, obj_key, key, vis_key, TEX, curve_tube, set_mat)

SKIN = (0.80, 0.48, 0.33)
SKIN_UNCLE = (0.72, 0.42, 0.28)


def _tex(n):
    return os.path.join(TEX, n)


def _collect(name):
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


class Character:
    def __init__(self, name, arm):
        self.name = name
        self.arm = arm
        self.eyes = []          # list of dict(root, pivot, lid_up, lid_lo, base_up, base_lo)
        self.parts = {}
        self.base_lids = (-20, 0)

    # ---- placement
    def place(self, frame, loc=None, rot_z=None, interp=None):
        a = self.arm
        if loc is not None:
            obj_key(a, frame, loc=loc, interp=interp)
        if rot_z is not None:
            a.rotation_euler = (0, 0, math.radians(rot_z))
            a.keyframe_insert("rotation_euler", frame=frame)

    def bone(self, b, frame, rot=None, loc=None, scale=None, interp=None):
        pose(self.arm, b, frame, rot=rot, loc=loc, scale=scale, interp=interp)

    # ---- face: lids in degrees. upper: -70 wide, -26 sleepy default, +62 closed. lower: 70 open, 48 default, 20 squint
    def lids(self, frame, up=None, lo=None, side=None, interp=None):
        for i, e in enumerate(self.eyes):
            if side is not None and i != side:
                continue
            if up is not None and e.get("lid_up"):
                obj_key(e["lid_up"], frame, rot=(up, 0, 0), interp=interp)
            if lo is not None and e.get("lid_lo"):
                obj_key(e["lid_lo"], frame, rot=(lo, 0, 0), interp=interp)

    def blink(self, frame, hold_up=None):
        up = self.base_lids[0] if hold_up is None else hold_up
        self.lids(frame - 2, up=up)
        self.lids(frame, up=62)
        self.lids(frame + 1, up=62)
        self.lids(frame + 4, up=up)

    def gaze(self, frame, x=0.0, z=0.0, interp=None):
        """x,z in degrees of eyeball rotation (x>0 looks to character's left)."""
        for e in self.eyes:
            obj_key(e["pivot"], frame, rot=(z, 0, x), interp=interp)

    def eye_scale(self, frame, s, interp=None):
        """Comedy 'big eyes' (FOMO) / pin eyes."""
        for e in self.eyes:
            obj_key(e["root"], frame, scale=(e["sx"] * s, s, s), interp=interp)

    def sparkle(self, frame, on):
        for e in self.eyes:
            if e.get("sparkle"):
                vis_key(e["sparkle"], frame, on)

    def walk(self, f0, f1, p0, p1, step_frames=8, heading=None, arms=True, lift=6, bounce=0.02):
        """FK walk: alternating steps, weight transfer bounce, counter arm swing."""
        a = self.arm
        p0, p1 = Vector(p0), Vector(p1)
        if heading is None:
            d = p1 - p0
            heading = math.degrees(math.atan2(-d.x, d.y)) + 180 if d.length > 1e-4 else 0
        a.rotation_euler = (0, 0, math.radians(heading))
        a.keyframe_insert("rotation_euler", frame=f0)
        n = max(1, int((f1 - f0) / step_frames))
        legs = self.legs
        for i in range(n + 1):
            f = f0 + i * step_frames
            t = i / n
            p = p0.lerp(p1, t)
            obj_key(a, f, loc=(p.x, p.y, p.z), interp="LINEAR")
            side = i % 2
            sw = 24 if 0 < i < n else 0
            for j, (th, sh, ft) in enumerate(legs):
                s = sw if j == side else -sw
                self.bone(th, f, rot=(s, 0, 0))
                self.bone(sh, f, rot=(0, 0, 0))
                # passing pose: knee lift on the swinging leg
                if i < n:
                    fm = f + step_frames // 2
                    self.bone(th, fm, rot=(-10 if j != side else 4, 0, 0))
                    self.bone(sh, fm, rot=(lift * 4 if j != side else 0, 0, 0))
            if arms and self.arms:
                for j, (ua, fa) in enumerate(self.arms):
                    s = -sw * 0.9 if j == side else sw * 0.9
                    self.bone(ua, f, rot=(s, 0, (-6 if j == 0 else 6)))
                    self.bone(fa, f, rot=(-abs(s) * 0.5 - 8, 0, 0))
            # bounce: down on contact, up on passing
            self.bone(self.hips, f, loc=(0, 0, -bounce), rot=(0, (4 if side else -4), 0))
            if i < n:
                self.bone(self.hips, f + step_frames // 2, loc=(0, bounce * 0.6, 0) if False else (0, 0, bounce * 0.6),
                          rot=(0, 0, 0))
        # settle
        self.bone(self.hips, f1 + 4, loc=(0, 0, 0), rot=(0, 0, 0))
        for th, sh, ft in legs:
            self.bone(th, f1 + 4, rot=(0, 0, 0))
            self.bone(sh, f1 + 4, rot=(0, 0, 0))

    def rest(self, frame):
        """Key every bone to rest (neutral stance) at frame."""
        for pb in self.arm.pose.bones:
            pose(self.arm, pb.name, frame, rot=(0, 0, 0), loc=(0, 0, 0), scale=(1, 1, 1))


# ======================================================================= eyes
def build_eye(char, name, center, normal, r, sx, mats, head_bone, lid_mat, lash_mat, iris_col,
              iris_r=0.62, lower=True, sparkle=True, sclera=None):
    """Eye unit oriented to face along `normal` (outward). Upper/lower lids are half
    domes rotating about local X; iris/pupil sit on a gaze pivot."""
    root = empty(f"{name}_root", center)
    n = Vector(normal).normalized()
    root.rotation_euler = (-n).to_track_quat("Y", "Z").to_euler()   # local -Y = outward
    root.scale = (sx, 1, 1)
    pivot = empty(f"{name}_gaze", (0, 0, 0), parent=root)
    pivot.rotation_mode = "XYZ"
    ball = sphere(f"{name}_ball", (0, 0, 0), r, m=eyeball_material(name, mats["iris_rgb"], r), seg=48, rings=24)
    ball.parent = pivot
    hl = sphere(f"{name}_hl", (r * 0.2, -r * 0.985, r * 0.2), r * 0.12, scale=(1, 0.25, 1), m=mats["hl"], seg=16,
                rings=8)
    hl.parent = pivot
    hl2 = sphere(f"{name}_hl2", (-r * 0.18, -r * 0.99, -r * 0.16), r * 0.055, scale=(1, 0.25, 1), m=mats["hl"],
                 seg=12, rings=6)
    hl2.parent = pivot
    sp = None
    if sparkle:  # star sparkle (FOMO) hidden by default
        sp = poly_prism(f"{name}_sparkle", [(math.cos(a) * (r * 0.42 if k % 2 == 0 else r * 0.14),
                                               math.sin(a) * (r * 0.42 if k % 2 == 0 else r * 0.14))
                                              for k, a in enumerate([i * math.pi / 4 + math.pi / 2 for i in range(8)])],
                        r * 0.02, m=mats["hl"], loc=(-r * 0.12, -r * 1.0, r * 0.12))
        sp.parent = pivot
        sp.hide_render = True
        sp.hide_viewport = True
    up = half_dome(f"{name}_lidU", r * 1.08, m=lid_mat)
    up.parent = root
    up.rotation_mode = "XYZ"
    lash = torus(f"{name}_lash", (0, 0, 0), r * 1.10, r * 0.15, m=lash_mat)
    # keep only the front half of the lash ring
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(lash.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y > r * 0.15], context="VERTS")
    bm.to_mesh(lash.data)
    bm.free()
    lash.parent = up
    lo = None
    if lower:
        lo = half_dome(f"{name}_lidL", r * 1.06, m=lid_mat, keep_upper=False)
        lo.parent = root
        lo.rotation_mode = "XYZ"
    bind(root, char.arm, head_bone)
    e = dict(root=root, pivot=pivot, lid_up=up, lid_lo=lo, sx=sx, sparkle=sp)
    char.eyes.append(e)
    return e


def eyeball_material(name, iris_rgb, r):
    """Sclera / limbal ring / iris (radial gradient) / pupil painted by angle from the eye's -Y axis."""
    m = bpy.data.materials.new(name + "_ballmat")
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    p = N["Principled BSDF"]
    p.inputs["Roughness"].default_value = 0.12
    p.inputs["Coat Weight"].default_value = 1.0
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Object"], sep.inputs[0])
    ny = N.new("ShaderNodeMath")
    ny.operation = "MULTIPLY"
    ny.inputs[1].default_value = -1.0 / r
    L.new(sep.outputs[1], ny.inputs[0])
    cr = N.new("ShaderNodeValToRGB")
    e = cr.color_ramp.elements
    ir, ig, ib = iris_rgb
    stops = [(0.0, (0.9, 0.9, 0.88)), (0.66, (0.9, 0.9, 0.88)), (0.685, (0.01, 0.01, 0.02)),
             (0.72, (ir * 0.6, ig * 0.6, ib * 0.6)), (0.88, (ir * 1.6, ig * 1.6, ib * 1.6)),
             (0.915, (ir, ig, ib)), (0.925, (0.0, 0.0, 0.005)), (1.0, (0.0, 0.0, 0.005))]
    e[0].position, e[0].color = stops[0][0], (*stops[0][1], 1)
    e[1].position, e[1].color = stops[1][0], (*stops[1][1], 1)
    for pos, col in stops[2:]:
        el = e.new(pos)
        el.color = (*col, 1)
    L.new(ny.outputs[0], cr.inputs[0])
    L.new(cr.outputs[0], p.inputs["Base Color"])
    return m


def _fist(name, loc, r, m, side, thumb=True):
    f = sphere(name, loc, r, scale=(0.9, 1.0, 1.05), m=m, seg=32, rings=16)
    parts = [f]
    # knuckle bumps + thumb
    for k in range(4):
        parts.append(sphere(f"{name}_k{k}", (loc[0] + side * r * 0.15, loc[1] - r * 0.72, loc[2] + r * (0.5 - k * 0.33)),
                            r * 0.32, m=m, seg=16, rings=8))
    if thumb:
        parts.append(sphere(f"{name}_thumb", (loc[0] - side * r * 0.55, loc[1] - r * 0.55, loc[2] + r * 0.15), r * 0.38,
                            scale=(0.8, 1, 1.2), m=m, seg=16, rings=8))
    return parts


def _sneaker(name, loc, size, upper, sole, side, xdecal=None, toe=None):
    x, y, z = loc
    w, l, h = size
    parts = [rbox(f"{name}_upper", (x, y - l * 0.08, z + h * 0.62), (w, l * 0.92, h), m=upper, round_=0.45),
             rbox(f"{name}_sole", (x, y - l * 0.06, z + h * 0.2), (w * 1.08, l * 1.02, h * 0.42), m=sole, round_=0.4)]
    if toe:
        parts.append(rbox(f"{name}_toe", (x, y - l * 0.43, z + h * 0.45), (w * 0.9, l * 0.2, h * 0.55), m=toe,
                          round_=0.5))
    # laces
    for k in range(3):
        parts.append(box(f"{name}_lace{k}", (x, y - l * (0.18 + k * 0.1), z + h * 1.12 - k * h * 0.08),
                         (w * 0.55, 0.012, 0.012), m=sole, bevel=0.004, rot=(0.4, 0, 0)))
    if xdecal:
        d = plane(f"{name}_x", (x + side * w * 0.53, y - l * 0.08, z + h * 0.68), (h * 0.7, h * 0.7), m=xdecal,
                  rot=(math.pi / 2, 0, side * math.pi / 2))
        parts.append(d)
    return parts


# ======================================================================= MR X
def build_mrx(prefix="MRX"):
    _collect(prefix)
    knit = mask_material(prefix)
    black_cloth = mat("mrx_cloth", (0.006, 0.006, 0.007), rough=0.8, bump=0.25, bump_scale=180, sheen=0.02, spec=0.22)
    skin = mat("mrx_skin", SKIN, rough=0.55, sss=0.15)
    shoe_b = mat("shoe_black", (0.02, 0.02, 0.022), rough=0.35, coat=0.3)
    shoe_w = mat("shoe_white", (0.85, 0.85, 0.83), rough=0.5)
    mats = dict(iris_rgb=(0.01, 0.12, 0.62),
                pupil=mat("pupil", (0.0, 0.0, 0.01), rough=0.1, coat=1.0),
                hl=emission_mat("eye_hl", (1, 1, 1), 6.0))
    lash = mat("lash", (0.01, 0.01, 0.01), rough=0.6)

    bones = [("root", (0, 0, 0), (0, 0, 0.1), None),
             ("hips", (0, 0, 0.38), (0, 0, 0.46), "root"),
             ("chest", (0, 0, 0.46), (0, 0, 0.68), "hips"),
             ("head", (0, 0, 0.68), (0, 0, 1.0), "chest")]
    for s, sx in (("L", 1), ("R", -1)):
        bones += [(f"uparm.{s}", (sx * 0.19, 0, 0.64), (sx * 0.235, 0, 0.53), "chest"),
                  (f"forearm.{s}", (sx * 0.235, 0, 0.53), (sx * 0.245, 0, 0.45), f"uparm.{s}"),
                  (f"hand.{s}", (sx * 0.245, 0, 0.45), (sx * 0.245, 0, 0.38), f"forearm.{s}"),
                  (f"thigh.{s}", (sx * 0.095, 0, 0.38), (sx * 0.095, 0, 0.22), "hips"),
                  (f"shin.{s}", (sx * 0.095, 0, 0.22), (sx * 0.095, 0, 0.07), f"thigh.{s}"),
                  (f"foot.{s}", (sx * 0.095, 0, 0.07), (sx * 0.095, -0.08, 0.04), f"shin.{s}")]
    arm = make_armature(prefix + "_rig", bones)
    c = Character(prefix, arm)
    c.hips = "hips"
    c.legs = [("thigh.L", "shin.L", "foot.L"), ("thigh.R", "shin.R", "foot.R")]
    c.arms = [("uparm.L", "forearm.L"), ("uparm.R", "forearm.R")]

    R = 0.36
    HC = (0, 0, 1.02)
    head = sphere(f"{prefix}_head", HC, R, m=knit, seg=96, rings=48)
    bind(head, arm, "head")
    # knit seam down the middle of the top (reference: vertical seam)
    seam = torus(f"{prefix}_seam", HC, R * 1.001, 0.004, m=mat("seam", (0.008, 0.008, 0.01), rough=0.9),
                 rot=(0, math.pi / 2, 0))
    import bmesh
    bm = bmesh.new(); bm.from_mesh(seam.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y < 0 and -v.co.x < R * 0.55], context="VERTS")
    bm.to_mesh(seam.data); bm.free()
    bind(seam, arm, "head")
    for s, sx, side in (("L", 1, 0), ("R", -1, 1)):
        nx, nz = 0.37 * sx, -0.15
        ny = -math.sqrt(1 - nx * nx - nz * nz)
        n = Vector((nx, ny, nz))
        ctr = Vector(HC) + n * R * 0.86
        build_eye(c, f"{prefix}_eye{s}", ctr, n, 0.064, 1.3, mats, "head", skin, lash, None)
    torso = rbox(f"{prefix}_shirt", (0, 0, 0.555), (0.40, 0.27, 0.30), m=black_cloth, round_=0.35)
    bind(torso, arm, "chest")
    collar = torus(f"{prefix}_collar", (0, 0, 0.70), 0.10, 0.018, m=black_cloth, scale=(1.2, 1, 1))
    bind(collar, arm, "chest")
    hips = rbox(f"{prefix}_pantsHip", (0, 0, 0.39), (0.37, 0.25, 0.11), m=black_cloth, round_=0.4)
    bind(hips, arm, "hips")
    for s, sx in (("L", 1), ("R", -1)):
        sl = rbox(f"{prefix}_sleeve{s}", (sx * 0.215, 0, 0.615), (0.13, 0.16, 0.13), m=black_cloth, round_=0.45,
                  rot=(0, sx * -0.3, 0))
        bind(sl, arm, f"uparm.{s}")
        ua = cyl(f"{prefix}_uarm{s}", (sx * 0.235, 0, 0.535), 0.043, 0.09, m=skin)
        bind(ua, arm, f"uparm.{s}")
        fa = cyl(f"{prefix}_farm{s}", (sx * 0.243, 0, 0.48), 0.047, 0.08, m=skin)
        bind(fa, arm, f"forearm.{s}")
        for p in _fist(f"{prefix}_fist{s}", (sx * 0.248, -0.005, 0.405), 0.062, skin, sx):
            bind(p, arm, f"hand.{s}")
        th = cyl(f"{prefix}_thigh{s}", (sx * 0.095, 0, 0.30), 0.088, 0.17, m=black_cloth)
        bind(th, arm, f"thigh.{s}")
        sh = cyl(f"{prefix}_shin{s}", (sx * 0.095, 0, 0.15), 0.084, 0.16, m=black_cloth)
        bind(sh, arm, f"shin.{s}")
        cuff = torus(f"{prefix}_cuff{s}", (sx * 0.095, 0, 0.085), 0.08, 0.022, m=black_cloth)
        bind(cuff, arm, f"shin.{s}")
        for p in _sneaker(f"{prefix}_shoe{s}", (sx * 0.10, -0.03, 0.0), (0.155, 0.28, 0.105), shoe_b, shoe_w, sx):
            bind(p, arm, f"foot.{s}")
    c.base_lids = (-26, 48)
    c.lids(1, up=-26, lo=48)
    return c


def mask_material(prefix):
    """Black knit mask with front/back marking textures projected in object space."""
    m = bpy.data.materials.new(prefix + "_mask")
    m.use_nodes = True
    nt = m.node_tree
    N = nt.nodes
    L = nt.links
    p = N["Principled BSDF"]
    p.inputs["Roughness"].default_value = 0.75
    p.inputs["Sheen Weight"].default_value = 0.04
    p.inputs["Specular IOR Level"].default_value = 0.22
    tc = N.new("ShaderNodeTexCoord")
    sc = N.new("ShaderNodeVectorMath")
    sc.operation = "SCALE"
    sc.inputs["Scale"].default_value = 1 / 0.36
    L.new(tc.outputs["Object"], sc.inputs[0])
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(sc.outputs[0], sep.inputs[0])

    def proj(img, flip):
        # u = (±x+1)/2, v = (z+1)/2
        mx = N.new("ShaderNodeMath")
        mx.operation = "MULTIPLY_ADD"
        mx.inputs[1].default_value = -0.5 if flip else 0.5
        mx.inputs[2].default_value = 0.5
        L.new(sep.outputs[0], mx.inputs[0])
        mz = N.new("ShaderNodeMath")
        mz.operation = "MULTIPLY_ADD"
        mz.inputs[1].default_value = 0.5
        mz.inputs[2].default_value = 0.5
        L.new(sep.outputs[2], mz.inputs[0])
        cx = N.new("ShaderNodeCombineXYZ")
        L.new(mx.outputs[0], cx.inputs[0])
        L.new(mz.outputs[0], cx.inputs[1])
        it = N.new("ShaderNodeTexImage")
        it.image = bpy.data.images.load(_tex(img), check_existing=True)
        it.extension = "EXTEND"
        L.new(cx.outputs[0], it.inputs[0])
        return it

    fr = proj("mrx_mask_front.png", False)
    bk = proj("mrx_mask_back.png", True)
    # front weight from -y
    fw = N.new("ShaderNodeMapRange")
    fw.inputs["From Min"].default_value = 0.10
    fw.inputs["From Max"].default_value = -0.25
    L.new(sep.outputs[1], fw.inputs["Value"])
    bw = N.new("ShaderNodeMapRange")
    bw.inputs["From Min"].default_value = 0.15
    bw.inputs["From Max"].default_value = 0.45
    L.new(sep.outputs[1], bw.inputs["Value"])
    black = (0.006, 0.006, 0.007, 1)
    mix1 = N.new("ShaderNodeMix")
    mix1.data_type = "RGBA"
    mix1.inputs[6].default_value = black
    L.new(fw.outputs[0], mix1.inputs[0])
    L.new(fr.outputs[0], mix1.inputs[7])
    mix2 = N.new("ShaderNodeMix")
    mix2.data_type = "RGBA"
    L.new(bw.outputs[0], mix2.inputs[0])
    L.new(mix1.outputs[2], mix2.inputs[6])
    L.new(bk.outputs[0], mix2.inputs[7])
    L.new(mix2.outputs[2], p.inputs["Base Color"])
    # knit rib bump (vertical wale pattern)
    wv = N.new("ShaderNodeTexWave")
    wv.wave_type = "BANDS"
    wv.bands_direction = "X"
    wv.inputs["Scale"].default_value = 90
    wv.inputs["Distortion"].default_value = 2
    L.new(tc.outputs["Object"], wv.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 400
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    add = N.new("ShaderNodeMath")
    L.new(wv.outputs["Fac"], add.inputs[0])
    L.new(nz.outputs["Fac"], add.inputs[1])
    bp = N.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.25
    bp.inputs["Distance"].default_value = 0.002
    L.new(add.outputs[0], bp.inputs["Height"])
    L.new(bp.outputs["Normal"], p.inputs["Normal"])
    # the white paint is slightly smoother than knit
    rr = N.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = 0.8
    rr.inputs["To Max"].default_value = 0.45
    L.new(mix2.outputs[2], rr.inputs["Value"])
    L.new(rr.outputs[0], p.inputs["Roughness"])
    return m


# ======================================================================= UNCLE
def head_material_uncle():
    """Skin with a skin-fade haircut on sides/back (darker as it goes up)."""
    m = bpy.data.materials.new("uncle_head")
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    p = N["Principled BSDF"]
    p.inputs["Roughness"].default_value = 0.5
    p.inputs["Subsurface Weight"].default_value = 0.15
    p.inputs["Subsurface Radius"].default_value = (0.9, 0.35, 0.2)
    p.inputs["Subsurface Scale"].default_value = 0.02
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Object"], sep.inputs[0])
    up = N.new("ShaderNodeMapRange")
    up.inputs["From Min"].default_value = -0.07
    up.inputs["From Max"].default_value = 0.09
    L.new(sep.outputs[2], up.inputs["Value"])
    # exclude the face (front, y < -0.15)
    fr = N.new("ShaderNodeMapRange")
    fr.inputs["From Min"].default_value = -0.12
    fr.inputs["From Max"].default_value = -0.05
    L.new(sep.outputs[1], fr.inputs["Value"])
    mul = N.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    L.new(up.outputs[0], mul.inputs[0])
    L.new(fr.outputs[0], mul.inputs[1])
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 600
    mul2 = N.new("ShaderNodeMath")
    mul2.operation = "MULTIPLY"
    L.new(mul.outputs[0], mul2.inputs[0])
    L.new(nz.outputs["Fac"], mul2.inputs[1])
    mx = N.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    mx.inputs[6].default_value = (*SKIN_UNCLE, 1)
    mx.inputs[7].default_value = (0.03, 0.022, 0.02, 1)
    sm = N.new("ShaderNodeMath")
    sm.operation = "MULTIPLY_ADD"
    sm.inputs[1].default_value = 2.2
    sm.inputs[2].default_value = 0.0
    L.new(mul2.outputs[0], sm.inputs[0])
    clamp = N.new("ShaderNodeClamp")
    L.new(sm.outputs[0], clamp.inputs[0])
    L.new(clamp.outputs[0], mx.inputs[0])
    L.new(mx.outputs[2], p.inputs["Base Color"])
    return m


def build_uncle(prefix="UNCLE"):
    _collect(prefix)
    skin = mat("uncle_skin", SKIN_UNCLE, rough=0.5, sss=0.15)
    hair = mat("uncle_hair", (0.004, 0.0035, 0.0035), rough=0.55, bump=0.9, bump_scale=700, spec=0.25)
    shirt = mat("uncle_shirt", (0.006, 0.006, 0.007), rough=0.8, bump=0.3, bump_scale=200, sheen=0.02, spec=0.25)
    apron = mat("uncle_apron", (0.022, 0.021, 0.024), rough=0.85, bump=0.5, bump_scale=120)
    leather = mat("leather", (0.28, 0.12, 0.04), rough=0.45, coat=0.2)
    brass = mat("brass", (0.75, 0.5, 0.2), rough=0.25, metal=1.0)
    frame_m = mat("glasses", (0.01, 0.01, 0.01), rough=0.15, coat=1.0)
    lens = mat("lens", (0.9, 0.9, 0.9), rough=0.02, spec=1.0)
    lens.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.12
    shoe_b = mat("shoe_black", (0.02, 0.02, 0.022), rough=0.35, coat=0.3)
    shoe_w = mat("shoe_white", (0.85, 0.85, 0.83), rough=0.5)
    xw = decal_mat("x_white", _tex("x_brush.png"))
    mats = dict(iris_rgb=(0.09, 0.045, 0.02),
                pupil=mat("pupil", (0.0, 0.0, 0.01), rough=0.1, coat=1.0),
                hl=emission_mat("eye_hl", (1, 1, 1), 6.0))
    lash = mat("lash", (0.01, 0.01, 0.01), rough=0.6)

    bones = [("root", (0, 0, 0), (0, 0, 0.1), None),
             ("hips", (0, 0, 0.40), (0, 0, 0.48), "root"),
             ("chest", (0, 0, 0.48), (0, 0, 0.80), "hips"),
             ("head", (0, 0, 0.80), (0, 0, 1.2), "chest"),
             ("jaw", (0, -0.15, 0.93), (0, -0.25, 0.93), "head")]
    for s, sx in (("L", 1), ("R", -1)):
        bones += [(f"uparm.{s}", (sx * 0.27, 0, 0.75), (sx * 0.32, 0, 0.60), "chest"),
                  (f"forearm.{s}", (sx * 0.32, 0, 0.60), (sx * 0.33, -0.01, 0.48), f"uparm.{s}"),
                  (f"hand.{s}", (sx * 0.33, -0.01, 0.48), (sx * 0.33, -0.01, 0.40), f"forearm.{s}"),
                  (f"thigh.{s}", (sx * 0.12, 0, 0.40), (sx * 0.12, 0, 0.23), "hips"),
                  (f"shin.{s}", (sx * 0.12, 0, 0.23), (sx * 0.12, 0, 0.08), f"thigh.{s}"),
                  (f"foot.{s}", (sx * 0.12, 0, 0.08), (sx * 0.12, -0.09, 0.04), f"shin.{s}")]
    arm = make_armature(prefix + "_rig", bones)
    c = Character(prefix, arm)
    c.hips = "hips"
    c.legs = [("thigh.L", "shin.L", "foot.L"), ("thigh.R", "shin.R", "foot.R")]
    c.arms = [("uparm.L", "forearm.L"), ("uparm.R", "forearm.R")]

    HC = Vector((0, 0, 1.04))
    head = rbox(f"{prefix}_head", HC, (0.50, 0.44, 0.44), m=head_material_uncle(), round_=0.42)
    bind(head, arm, "head")
    jowl = rbox(f"{prefix}_cheeks", HC + Vector((0, -0.02, -0.11)), (0.50, 0.42, 0.20), m=skin, round_=0.48)
    bind(jowl, arm, "head")
    top = rbox(f"{prefix}_hairtop", HC + Vector((0, 0.005, 0.235)), (0.50, 0.445, 0.25), m=hair, round_=0.16)
    bind(top, arm, "head")
    # flat-top front ridge (pompadour edge)
    ridge = rbox(f"{prefix}_hairfront", HC + Vector((0, -0.175, 0.26)), (0.51, 0.13, 0.24), m=hair, round_=0.3)
    bind(ridge, arm, "head")
    for s, sx in (("L", 1), ("R", -1)):
        ear = sphere(f"{prefix}_ear{s}", HC + Vector((sx * 0.255, 0.02, -0.02)), 0.065, scale=(0.5, 0.8, 1.05),
                     m=skin)
        bind(ear, arm, "head")
        n = Vector((sx * 0.42, -1, 0.05)).normalized()
        ctr = HC + Vector((sx * 0.105, -0.205, 0.035))
        e = build_eye(c, f"{prefix}_eye{s}", ctr, n, 0.05, 1.2, mats, "head", skin, lash, None, iris_r=0.62,
                      sparkle=False)
        # thick angled brow
        brow = rbox(f"{prefix}_brow{s}", ctr + Vector((sx * 0.01, -0.045, 0.092)), (0.15, 0.05, 0.05), m=hair, round_=0.5,
                    rot=(0, sx * 0.18, 0))
        bind(brow, arm, "head")
        c.parts[f"brow{s}"] = brow
        # glasses rims (rectangular)
        gx, gz = ctr.x, ctr.z + 0.005
        gy = -0.272
        w, h, t = 0.16, 0.115, 0.02
        for nm, loc, size in (("t", (gx, gy, gz + h / 2), (w, t, t * 1.4)), ("b", (gx, gy, gz - h / 2), (w, t, t)),
                              ("o", (gx + sx * w / 2, gy, gz), (t * 1.2, t, h)),
                              ("i", (gx - sx * w / 2, gy, gz), (t, t, h))):
            r_ = box(f"{prefix}_glass{s}{nm}", Vector(loc), size, m=frame_m,
                     bevel=0.004)
            bind(r_, arm, "head")
        ln = box(f"{prefix}_lens{s}", Vector((gx, gy + 0.002, gz)), (w - 0.01, 0.003, h - 0.01), m=lens)
        bind(ln, arm, "head")
        c.parts[f"lens{s}"] = ln
        temple = box(f"{prefix}_temple{s}", Vector((sx * 0.255, -0.12, gz + 0.03)), (0.014, 0.30, 0.016),
                     m=frame_m, bevel=0.003)
        bind(temple, arm, "head")
    bridge = box(f"{prefix}_bridge", Vector((0, -0.272, HC.z + 0.06)), (0.06, 0.016, 0.016), m=frame_m, bevel=0.003)
    bind(bridge, arm, "head")
    nose = sphere(f"{prefix}_nose", HC + Vector((0, -0.25, -0.035)), 0.05, scale=(1.0, 0.9, 0.85), m=skin)
    bind(nose, arm, "head")
    # mouth (dark), opened by jaw bone scale; moustache sits on top
    mouth = sphere(f"{prefix}_mouth", HC + Vector((0, -0.215, -0.14)), 0.05, scale=(1.2, 0.5, 0.12),
                   m=mat("mouth", (0.08, 0.01, 0.015), rough=0.6))
    bind(mouth, arm, "jaw")
    teeth = box(f"{prefix}_teeth", HC + Vector((0, -0.235, -0.115)), (0.07, 0.01, 0.014),
                m=mat("teeth", (0.9, 0.88, 0.82), rough=0.3), bevel=0.004)
    bind(teeth, arm, "jaw")
    c.parts["mouth"] = mouth
    must_pts = []
    for i in range(25):
        t = i / 24
        x = -0.16 + 0.32 * t
        z = 0.045 * math.sin(math.pi * t) ** 0.6 - 0.035 * abs(x) / 0.16
        must_pts.append((x, z))
    for i in range(24, -1, -1):
        t = i / 24
        x = -0.16 + 0.32 * t
        must_pts.append((x * 0.98, -0.045 - 0.03 * (abs(x) / 0.16) ** 2 + 0.008 * math.cos(x * 60)))
    must = poly_prism(f"{prefix}_moustache", must_pts, 0.07, m=hair, loc=tuple(HC + Vector((0, -0.235, -0.085))))
    sub = must.modifiers.new("subd", "SUBSURF")
    sub.levels = sub.render_levels = 2
    bind(must, arm, "head")
    c.parts["moustache"] = must

    torso = rbox(f"{prefix}_shirt", (0, 0, 0.62), (0.52, 0.34, 0.38), m=shirt, round_=0.3)
    bind(torso, arm, "chest")
    collar = rbox(f"{prefix}_collar", (0, -0.06, 0.815), (0.30, 0.22, 0.05), m=shirt, round_=0.4)
    bind(collar, arm, "chest")
    ap = rbox(f"{prefix}_apron", (0, -0.17, 0.52), (0.46, 0.04, 0.52), m=apron, round_=0.25, sub=1)
    bind(ap, arm, "chest")
    xd = plane(f"{prefix}_apronX", (0, -0.197, 0.70), (0.13, 0.13), m=xw, rot=(math.pi / 2, 0, 0))
    bind(xd, arm, "chest")
    pocket = box(f"{prefix}_pocket", (0, -0.193, 0.47), (0.36, 0.012, 0.14), m=apron, bevel=0.005)
    bind(pocket, arm, "chest")
    for k, px in enumerate((-0.14, -0.12, 0.11)):
        pen = cyl(f"{prefix}_pen{k}", (px, -0.196, 0.55), 0.008, 0.08, m=brass if k != 1 else leather)
        bind(pen, arm, "chest")
    for s, sx in (("L", 1), ("R", -1)):
        strap = box(f"{prefix}_strap{s}", (sx * 0.16, -0.12, 0.79), (0.04, 0.16, 0.012), m=leather, bevel=0.004,
                    rot=(0.9, 0, 0))
        bind(strap, arm, "chest")
        rivet = sphere(f"{prefix}_rivet{s}", (sx * 0.16, -0.198, 0.76), 0.012, m=brass)
        bind(rivet, arm, "chest")
        sl = rbox(f"{prefix}_sleeve{s}", (sx * 0.295, 0, 0.72), (0.16, 0.20, 0.15), m=shirt, round_=0.4)
        bind(sl, arm, f"uparm.{s}")
        roll = torus(f"{prefix}_roll{s}", (sx * 0.31, 0, 0.64), 0.075, 0.022, m=shirt)
        bind(roll, arm, f"uparm.{s}")
        fa = cyl(f"{prefix}_farm{s}", (sx * 0.325, -0.005, 0.56), 0.058, 0.13, m=skin)
        bind(fa, arm, f"forearm.{s}")
        for p in _fist(f"{prefix}_fist{s}", (sx * 0.335, -0.012, 0.455), 0.072, skin, sx):
            bind(p, arm, f"hand.{s}")
        th = cyl(f"{prefix}_thigh{s}", (sx * 0.12, 0, 0.32), 0.11, 0.18, m=shirt)
        bind(th, arm, f"thigh.{s}")
        cp = box(f"{prefix}_cargo{s}", (sx * 0.225, 0, 0.29), (0.03, 0.11, 0.10), m=shirt, bevel=0.01)
        bind(cp, arm, f"thigh.{s}")
        sh = cyl(f"{prefix}_shin{s}", (sx * 0.12, 0, 0.16), 0.105, 0.16, m=shirt)
        bind(sh, arm, f"shin.{s}")
        for p in _sneaker(f"{prefix}_shoe{s}", (sx * 0.12, -0.02, 0.0), (0.16, 0.27, 0.10), shoe_b, shoe_w, sx,
                          xdecal=xw):
            bind(p, arm, f"foot.{s}")
    hipb = rbox(f"{prefix}_pantsHip", (0, 0, 0.42), (0.47, 0.32, 0.12), m=shirt, round_=0.35)
    bind(hipb, arm, "hips")
    watch = cyl(f"{prefix}_watch", (0.33, -0.005, 0.53), 0.064, 0.03, m=frame_m)
    bind(watch, arm, "forearm.L")
    face = cyl(f"{prefix}_watchface", (0.33 + 0.0, -0.07, 0.53), 0.026, 0.012, m=mat("watchface", (0.05, 0.05, 0.06),
                                                                                       rough=0.1, metal=0.5),
               rot=(math.pi / 2, 0, 0))
    bind(face, arm, "forearm.L")
    c.base_lids = (-22, 50)
    c.lids(1, up=-22, lo=50)
    return c


def uncle_mouth(c, frame, openv, smile=0.0, interp=None):
    """openv 0..1 (jaw), smile -1..1 (moustache corners lift via scale/rot)."""
    pose(c.arm, "jaw", frame, scale=(1 + 0.15 * openv + 0.1 * smile, 1, 1 + 2.4 * openv), interp=interp)
    must = c.parts["moustache"]
    obj_key(must, frame, scale=(1 + 0.08 * smile, 1, 1 + 0.10 * openv), interp=interp)


def uncle_brows(c, frame, l=0.0, r=0.0, angle=0.0, interp=None):
    """Raise (+) / lower (-) brows in cm-ish units; angle>0 = angry inward slope."""
    for s, v, sx in (("L", l, 1), ("R", r, -1)):
        b = c.parts[f"brow{s}"]
        if not hasattr(b, "_base"):
            pass
        base = b.get("base_z")
        if base is None:
            b["base_z"] = b.location.z
            b["base_ry"] = b.rotation_euler.y
            base = b["base_z"]
        b.location.z = base + v * 0.01
        b.rotation_euler.y = b["base_ry"] + sx * math.radians(angle)
        b.keyframe_insert("location", index=2, frame=frame)
        b.keyframe_insert("rotation_euler", index=1, frame=frame)


# ======================================================================= X-BOT
def build_xbot(prefix="XBOT"):
    _collect(prefix)
    gloss = mat("xbot_gloss", (0.012, 0.012, 0.014), rough=0.08, coat=1.0, spec=0.6)
    panel = mat("xbot_panel", (0.006, 0.006, 0.008), rough=0.04, coat=1.0)
    gold = mat("gold", (0.95, 0.68, 0.25), rough=0.18, metal=1.0)
    goldglow = mat("goldglow", (0.9, 0.6, 0.2), rough=0.2, metal=0.6, emit=(1.0, 0.6, 0.15), emit_str=2.5)
    eye_m = emission_mat("xbot_eye", (1.0, 0.62, 0.05), 9.0)
    eye_core = emission_mat("xbot_eye_core", (1.0, 0.85, 0.3), 14.0)
    rubber = mat("xbot_arm", (0.015, 0.015, 0.017), rough=0.3, coat=0.5)
    glove = mat("glove", (0.92, 0.92, 0.9), rough=0.55, sheen=0.1)
    shoe_b = mat("shoe_black", (0.02, 0.02, 0.022), rough=0.35, coat=0.3)
    shoe_w = mat("shoe_white", (0.85, 0.85, 0.83), rough=0.5)
    xw = decal_mat("x_white", _tex("x_brush.png"))

    bones = [("root", (0, 0, 0), (0, 0, 0.1), None),
             ("body", (0, 0, 0.36), (0, 0, 0.70), "root"),
             ("cap", (0, 0, 1.0), (0, 0, 1.2), "body")]
    for s, sx in (("L", 1), ("R", -1)):
        bones += [(f"uparm.{s}", (sx * 0.31, 0, 0.66), (sx * 0.40, 0, 0.55), "body"),
                  (f"forearm.{s}", (sx * 0.40, 0, 0.55), (sx * 0.40, -0.02, 0.42), f"uparm.{s}"),
                  (f"hand.{s}", (sx * 0.40, -0.02, 0.42), (sx * 0.40, -0.02, 0.34), f"forearm.{s}"),
                  (f"thigh.{s}", (sx * 0.12, 0, 0.40), (sx * 0.12, 0, 0.24), "root"),
                  (f"shin.{s}", (sx * 0.12, 0, 0.24), (sx * 0.12, 0, 0.09), f"thigh.{s}"),
                  (f"foot.{s}", (sx * 0.12, 0, 0.09), (sx * 0.12, -0.09, 0.05), f"shin.{s}")]
    arm = make_armature(prefix + "_rig", bones)
    c = Character(prefix, arm)
    c.hips = "body"
    c.legs = [("thigh.L", "shin.L", "foot.L"), ("thigh.R", "shin.R", "foot.R")]
    c.arms = [("uparm.L", "forearm.L"), ("uparm.R", "forearm.R")]

    body = box(f"{prefix}_body", (0, 0, 0.70), (0.64, 0.30, 0.62), m=gloss, bevel=0.07, seg=1)
    bind(body, arm, "body")
    # inset front panel and glowing gold edge
    pn = box(f"{prefix}_panel", (0, -0.152, 0.70), (0.50, 0.01, 0.48), m=panel, bevel=0.02, seg=2)
    bind(pn, arm, "body")
    for nm, loc, size in (("t", (0, -0.155, 0.945), (0.52, 0.008, 0.008)), ("b", (0, -0.155, 0.455), (0.52, 0.008, 0.008)),
                          ("l", (0.258, -0.155, 0.70), (0.008, 0.008, 0.50)),
                          ("r", (-0.258, -0.155, 0.70), (0.008, 0.008, 0.50))):
        e = box(f"{prefix}_edge{nm}", loc, size, m=goldglow)
        bind(e, arm, "body")
    # outer chamfer gold rim lines (front & back outline glow like reference)
    for yv in (-0.151, 0.151):
        for nm, loc, size in (("t", (0, yv, 1.012), (0.50, 0.006, 0.006)), ("b", (0, yv, 0.388), (0.50, 0.006, 0.006)),
                              ("l", (0.322, yv, 0.70), (0.006, 0.006, 0.48)),
                              ("r", (-0.322, yv, 0.70), (0.006, 0.006, 0.48))):
            e = box(f"{prefix}_rim{nm}{yv}", loc, size, m=goldglow)
            bind(e, arm, "body")
    # angry eyes (flat glowing shapes on the panel)
    for s, sx in (("L", 1), ("R", -1)):
        pts = [(-0.075, 0.03), (0.075, -0.005), (0.06, -0.03), (0.02, -0.055), (-0.03, -0.055), (-0.07, -0.02)]
        pts = [(-sx * x, z) for x, z in pts]   # inner corners low = angry slant (reference)
        if sx > 0:
            pts = pts[::-1]
        eye = poly_prism(f"{prefix}_eye{s}", pts, 0.008, m=eye_m, loc=(sx * 0.105, -0.16, 0.79))
        core = poly_prism(f"{prefix}_eyecore{s}", [(x * 0.45, z * 0.45 - 0.008) for x, z in pts], 0.004, m=eye_core,
                          loc=(0, -0.0045, 0))
        core.parent = eye
        bind(eye, arm, "body")
        c.parts[f"eye{s}"] = eye
        c.eyes.append(dict(root=eye, pivot=eye, sx=1.0))
    xd = plane(f"{prefix}_X", (0, -0.159, 0.58), (0.19, 0.19), m=xw, rot=(math.pi / 2, 0, 0))
    bind(xd, arm, "body")
    c.parts["X"] = xd
    collar = cyl(f"{prefix}_collar", (0, 0, 1.02), 0.12, 0.04, m=gloss, bevel=0.01)
    bind(collar, arm, "cap")
    ring = cyl(f"{prefix}_ring", (0, 0, 1.06), 0.105, 0.065, m=gold, bevel=0.008)
    bind(ring, arm, "cap")
    cap = cyl(f"{prefix}_cap", (0, 0, 1.17), 0.215, 0.17, m=gloss, bevel=0.03, verts=64)
    bind(cap, arm, "cap")
    capx = plane(f"{prefix}_capX", (0, -0.217, 1.17), (0.12, 0.12), m=xw, rot=(math.pi / 2, 0, 0))
    bind(capx, arm, "cap")
    for s, sx in (("L", 1), ("R", -1)):
        up = cyl(f"{prefix}_uarm{s}", (sx * 0.355, 0, 0.605), 0.03, 0.15, m=rubber, rot=(0, sx * 0.7, 0))
        bind(up, arm, f"uparm.{s}")
        sj = sphere(f"{prefix}_elbow{s}", (sx * 0.40, 0, 0.55), 0.031, m=rubber)
        bind(sj, arm, f"uparm.{s}")
        fa = cyl(f"{prefix}_farm{s}", (sx * 0.40, -0.01, 0.485), 0.03, 0.13, m=rubber)
        bind(fa, arm, f"forearm.{s}")
        cuff = torus(f"{prefix}_cuff{s}", (sx * 0.40, -0.02, 0.435), 0.045, 0.02, m=glove)
        bind(cuff, arm, f"hand.{s}")
        fist = _fist(f"{prefix}_glove{s}", (sx * 0.40, -0.025, 0.375), 0.07, glove, sx)
        for p in fist:
            bind(p, arm, f"hand.{s}")
        # pointing glove (hidden by default): palm + extended index finger
        pg = sphere(f"{prefix}_point{s}", (sx * 0.40, -0.025, 0.375), 0.062, scale=(0.9, 1, 1), m=glove)
        fing = cyl(f"{prefix}_finger{s}", (sx * 0.40, -0.025, 0.27), 0.022, 0.13, m=glove)
        tip = sphere(f"{prefix}_fingertip{s}", (sx * 0.40, -0.025, 0.205), 0.022, m=glove)
        th = sphere(f"{prefix}_pthumb{s}", (sx * 0.40 - sx * 0.04, -0.06, 0.39), 0.026, m=glove)
        fing.parent = pg
        tip.parent = pg
        th.parent = pg
        fing.matrix_parent_inverse = pg.matrix_world.inverted()
        tip.matrix_parent_inverse = pg.matrix_world.inverted()
        th.matrix_parent_inverse = pg.matrix_world.inverted()
        bind(pg, arm, f"hand.{s}")
        c.parts[f"fist{s}"] = fist[0]
        c.parts[f"fistparts{s}"] = fist
        c.parts[f"point{s}"] = pg
        for o in [pg, fing, tip, th]:
            o.hide_render = True
            o.hide_viewport = True
        lg = cyl(f"{prefix}_leg{s}", (sx * 0.12, 0, 0.25), 0.032, 0.30, m=rubber)
        bind(lg, arm, f"thigh.{s}")
        for p in _sneaker(f"{prefix}_shoe{s}", (sx * 0.13, -0.02, 0.0), (0.16, 0.26, 0.10), shoe_b, shoe_w, sx,
                          xdecal=xw, toe=shoe_w):
            bind(p, arm, f"foot.{s}")
    return c


def xbot_point(c, frame, side, on):
    """Swap fist <-> pointing glove on side 'L'/'R'."""
    for p in c.parts[f"fistparts{side}"]:
        p.hide_render = on
        p.hide_viewport = on
        p.keyframe_insert("hide_render", frame=frame)
        p.keyframe_insert("hide_viewport", frame=frame)
    vis_key(c.parts[f"point{side}"], frame, on)


def xbot_eyes(c, frame, open_=1.0, angry=0.0, size=1.0, interp=None):
    """open_ scales eye height (0.1 = slit), angry tilts eyes inward, size = comedic scale."""
    for s, sx in (("L", 1), ("R", -1)):
        e = c.parts[f"eye{s}"]
        e.rotation_euler.y = math.radians(-sx * angry * 14)
        e.scale = (size, 1, max(0.05, open_) * size)
        e.keyframe_insert("rotation_euler", index=1, frame=frame)
        e.keyframe_insert("scale", frame=frame)
