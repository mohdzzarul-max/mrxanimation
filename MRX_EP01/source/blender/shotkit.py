"""Shot framework + acting helpers shared by all shot implementations."""
import json, math, os, random, sys
import numpy as np
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import timeline as TL  # noqa
from lib import (ROOT, camera, cam_key, pose, obj_key, vis_key, bind, set_interp_at, _fcurves_for, key, empty,
                 area, point, spot, mat, emission_mat, decal_mat, plane, sphere, cyl, box, rbox, TEX)
import characters as C
import envs as E

DUR = json.load(open(os.path.join(ROOT, "voices", "durations.json")))
SPEC = {s["id"]: s for s in TL.SHOTS}


def F(local):
    """local shot frame (0-based) -> Blender frame (1-based)."""
    return int(round(local)) + 1


class Ctx:
    def __init__(self, sid):
        self.sid = sid
        self.spec = SPEC[sid]
        self.n = self.spec["frames"]
        self.sc = bpy.context.scene
        self.chars = {}
        self.H = {}

    def line(self, lid, nth=0):
        """(start_local, length_frames) of a dialogue cue in this shot."""
        hits = [l for l in self.spec["lines"] if l[0] == lid]
        lid_, st, tempo = hits[nth]
        return st, int(math.ceil(DUR[lid] / tempo * TL.FPS))

    def cam(self, lens=50, fstop=2.8):
        cam, tgt, foc = camera("Cam", lens=lens, focus=(0, 0, 0), fstop=fstop)
        self.camo, self.tgt, self.foc = cam, tgt, foc
        return cam

    def ck(self, f, pos, look, lens=None, focus=None, interp=None):
        cam_key(self.camo, self.tgt, F(f), pos, look, interp=interp, lens=lens)
        if focus is not None:
            obj_key(self.foc, F(f), loc=focus, interp=interp)

    def hold_cut(self, f):
        """Make the camera keys at local frame f constant (next key becomes a hard cut)."""
        for o, p in ((self.camo, "location"), (self.tgt, "location"), (self.foc, "location")):
            set_interp_at(o, p, F(f), "CONSTANT")
        set_interp_at(self.camo.data, "lens", F(f), "CONSTANT")


# ------------------------------------------------------------------ scene assembly
def setup(sid, env, chars=(), res=(360, 640), samples=6):
    from lib import new_scene
    sc = new_scene(res=res, samples=samples)
    sc.render.use_motion_blur = False
    ctx = Ctx(sid)
    ctx.H = {"booth": E.booth, "bedroom": E.bedroom, "storeroom": E.storeroom, "runway": E.runway,
             "void": E.void}[env]()
    for nm in chars:
        ctx.chars[nm] = {"MRX": C.build_mrx, "UNCLE": C.build_uncle, "XBOT": C.build_xbot}[nm]()
    for o in bpy.data.objects:
        for md in getattr(o, "modifiers", []):
            if md.type == "SUBSURF":
                md.render_levels = min(md.render_levels, 2)
    a, b = ctx.spec["render"]
    sc.frame_start, sc.frame_end = F(a), F(b - 1)
    return ctx


# ------------------------------------------------------------------ posing helpers (verified rig axes)
# arm forward = -X on uparm; elbow bend forward = -X on forearm; sideways out: L -> -Z, R -> +Z
def arm(c, side, f, fwd=0, out=0, elbow=0, twist=0, hand=(0, 0, 0), interp=None):
    o = -out if side == "L" else out
    pose(c.arm, f"uparm.{side}", F(f), rot=(-fwd, twist, o), interp=interp)
    pose(c.arm, f"forearm.{side}", F(f), rot=(-elbow, 0, 0), interp=interp)
    pose(c.arm, f"hand.{side}", F(f), rot=hand, interp=interp)


def arms_rest(c, f, interp=None):
    for s in "LR":
        arm(c, s, f, fwd=4, out=6, elbow=6, interp=interp)


def head(c, f, nod=0, turn=0, tilt=0, interp=None, bone="head"):
    """nod>0 looks down, turn>0 turns to character's left, tilt>0 rolls toward character's right."""
    pose(c.arm, bone, F(f), rot=(nod, turn, tilt), interp=interp)


def chest(c, f, lean=0, turn=0, tilt=0, interp=None):
    pose(c.arm, "chest" if "chest" in c.arm.pose.bones else "body", F(f), rot=(lean, turn, tilt), interp=interp)


def hips(c, f, loc=(0, 0, 0), rot=(0, 0, 0), interp=None):
    pose(c.arm, c.hips, F(f), loc=loc, rot=rot, interp=interp)


def legs(c, f, l=(0, 0), r=(0, 0), interp=None):
    """(thigh fwd deg, knee bend deg) per leg. Thigh forward = -X, knee bend = +X on shin."""
    for s, (t, k) in (("L", l), ("R", r)):
        pose(c.arm, f"thigh.{s}", F(f), rot=(-t, 0, 0), interp=interp)
        pose(c.arm, f"shin.{s}", F(f), rot=(k, 0, 0), interp=interp)


def place(c, f, loc, rot_z=None, interp=None):
    obj_key(c.arm, F(f), loc=loc, interp=interp)
    if rot_z is not None:
        obj_key(c.arm, F(f), rot=(0, 0, rot_z), interp=interp)


def face_dir(p_from, p_to):
    """rot_z (deg) so a character at p_from faces p_to (rest faces -Y)."""
    d = Vector(p_to) - Vector(p_from)
    return math.degrees(math.atan2(d.x, -d.y))


def sit(c, f, seat_drop=-0.05, interp=None):
    legs(c, f, l=(88, 88), r=(88, 88), interp=interp)
    hips(c, f, loc=(0, 0, seat_drop), interp=interp)


def sit_floor(c, f, interp=None):
    legs(c, f, l=(84, 10), r=(80, 14), interp=interp)
    hips(c, f, loc=(0, -0.0, -0.30), interp=interp)


# ------------------------------------------------------------------ expressions
EXPR = {  # MR X lids: (upper, lower, roll) roll>0 = angry slant (inner corners down)
    "neutral": (-26, 48, 0), "wide": (-72, 74, 0), "excited": (-58, 64, 0), "happy": (-40, 30, -6),
    "suspicious": (-4, 30, 0), "squint": (6, 24, 0), "angry": (-16, 40, 16), "furious": (-30, 50, 22),
    "sad": (-14, 50, -16), "embarrassed": (-8, 44, -12), "closed": (62, 48, 0), "smug": (-6, 36, 8),
    "shock": (-80, 80, 0),
}


def expr(c, f, name, interp=None):
    up, lo, roll = getattr(c, "EXPR", EXPR)[name]
    for i, e in enumerate(c.eyes):
        sgn = 1 if i == 0 else -1  # eye0 = character's left (+X)
        if e.get("lid_up"):
            obj_key(e["lid_up"], F(f), rot=(up, 0, sgn * roll), interp=interp)
        if e.get("lid_lo"):
            obj_key(e["lid_lo"], F(f), rot=(lo, 0, 0), interp=interp)
    c._expr = name


def blink(c, f, name=None):
    name = name or getattr(c, "_expr", "neutral")
    up, lo, roll = getattr(c, "EXPR", EXPR)[name]
    for i, e in enumerate(c.eyes):
        sgn = 1 if i == 0 else -1
        if not e.get("lid_up"):
            continue
        for ff, u in ((f - 1, up), (f + 1, 60), (f + 2, 60), (f + 5, up)):
            obj_key(e["lid_up"], F(ff), rot=(u, 0, sgn * roll))


def blinks(c, f0, f1, every=(55, 95), seed=1):
    rnd = random.Random(seed)
    f = f0 + rnd.randint(10, 30)
    while f < f1 - 6:
        blink(c, f)
        f += rnd.randint(*every)


def gaze(c, f, x=0, z=0, interp=None):
    """x>0 looks to character's left, z>0 looks up (deg)."""
    for e in c.eyes:
        if e["pivot"] is not e["root"]:
            obj_key(e["pivot"], F(f), rot=(-z, 0, x), interp=interp)


def eye_size(c, f, s, interp=None):
    if getattr(c, "recessed", False):
        s = min(max(s, 0.94), 1.04)     # recessed eyes must never grow past the mask surface
    for e in c.eyes:
        sx = e["sx"]
        obj_key(e["root"], F(f), scale=(sx * s, s, s), interp=interp)


def sparkle(c, f, on):
    for e in c.eyes:
        if e.get("sparkle"):
            vis_key(e["sparkle"], F(f), on)


def xeyes(c, f, open_=1.0, angry=0.0, size=1.0, interp=None):
    for s, sx in (("L", 1), ("R", -1)):
        e = c.parts[f"eye{s}"]
        e.rotation_euler.y = math.radians(-sx * angry * 14)
        e.scale = (size, 1, max(0.05, open_) * size)
        e.keyframe_insert("rotation_euler", index=1, frame=F(f))
        e.keyframe_insert("scale", frame=F(f))
        if interp:
            set_interp_at(e, "scale", F(f), interp)


def xpoint(c, f, side, on):
    C.xbot_point(c, F(f), side, on)


def brows(c, f, l=0.0, r=0.0, angle=0.0):
    C.uncle_brows(c, F(f), l=l, r=r, angle=angle)


def smile(c, f, v, openv=0.0):
    C.uncle_mouth(c, F(f), openv, smile=v)


# ------------------------------------------------------------------ audio-driven acting
def envelope(lid, tempo=1.0):
    import soundfile as sf
    w, sr = sf.read(os.path.join(ROOT, "voices", lid + ".wav"))
    if w.ndim > 1:
        w = w.mean(1)
    hop = int(sr / TL.FPS / tempo)
    n = int(len(w) / hop) + 1
    env = np.array([np.sqrt(np.mean(w[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(n)])
    env = env / (env.max() + 1e-9)
    return env


def lipsync(c, ctx, lid, nth=0, smile_v=0.3, nods=True, gain=1.0):
    """Uncle: jaw/moustache from voice RMS every 2 frames; head nods on stressed syllables."""
    st, ln = ctx.line(lid, nth)
    tempo = [l for l in ctx.spec["lines"] if l[0] == lid][nth][2]
    env = envelope(lid, tempo)
    smile(c, st - 2, smile_v, 0)
    for i in range(0, len(env), 2):
        v = min(1.0, env[i] * 1.3 * gain)
        v = 0 if v < 0.12 else v
        smile(c, st + i, smile_v, v * 0.9)
    smile(c, st + len(env) + 1, smile_v, 0)


def talk_bob(c, ctx, lid, nth=0, amp=1.0, bone="head"):
    """Masked MR X / bottle X-BOT have no mouths: squash-and-stretch on syllables keeps them alive."""
    st, ln = ctx.line(lid, nth)
    tempo = [l for l in ctx.spec["lines"] if l[0] == lid][nth][2]
    env = envelope(lid, tempo)
    pose(c.arm, bone, F(st - 1), scale=(1, 1, 1))
    for i in range(0, len(env), 2):
        v = env[i] * amp
        s = 1 + 0.035 * v
        pose(c.arm, bone, F(st + i), scale=(s, 2 - s, 2 - s * 0.98) if bone == "body" else (s, 2 - s, s))
    pose(c.arm, bone, F(st + len(env) + 2), scale=(1, 1, 1))


# ------------------------------------------------------------------ procedural layers (F-curve noise)
def _noise(id_data, path_prefix, strength, scale, phase=0.0, indices=(0, 1, 2)):
    for fc in _fcurves_for(id_data):
        if fc.data_path == path_prefix and fc.array_index in indices:
            m = fc.modifiers.new("NOISE")
            m.strength = strength
            m.scale = scale
            m.phase = phase + fc.array_index * 7.3
            m.blend_type = "ADD"


def life(c, strength=1.0, seed=0):
    """Breathing + micro head drift added on top of keyed animation."""
    a = c.arm
    # make sure channels exist
    for bn in [b for b in ("head", "chest", "body") if b in a.pose.bones]:
        pb = a.pose.bones[bn]
        if not any(fc.data_path == f'pose.bones["{bn}"].rotation_euler' for fc in _fcurves_for(a)):
            pb.keyframe_insert("rotation_euler", frame=1)
        _noise(a, f'pose.bones["{bn}"].rotation_euler', math.radians(1.6 * strength), 28, seed)


def handheld(ctx, strength=0.006, scale=22):
    cam = ctx.camo
    if not any(fc.data_path == "location" for fc in _fcurves_for(cam)):
        cam.keyframe_insert("location", frame=1)
    _noise(cam, "location", strength, scale)
    t = ctx.tgt
    if not any(fc.data_path == "location" for fc in _fcurves_for(t)):
        t.keyframe_insert("location", frame=1)
    _noise(t, "location", strength * 0.7, scale, 3.1)


# ------------------------------------------------------------------ props in hands
def hand_pos(c, side):
    b = c.arm.data.bones[f"hand.{side}"]
    return Vector(c.arm.matrix_world @ ((b.head_local + b.tail_local) / 2))


def hold(c, side, prop_root, offset=(0, -0.06, -0.02), rot=(0, 0, 0)):
    """Bind a prop to a hand bone. Call before moving/animating the character (rest pose)."""
    p = hand_pos(c, side) + Vector(offset)
    prop_root.location = p
    prop_root.rotation_euler = [math.radians(x) for x in rot]
    bind(prop_root, c.arm, f"hand.{side}")
    return prop_root


def show(o, f, on):
    vis_key(o, F(f), on)


def light_key(lo, f, energy=None, color=None, interp=None):
    if energy is not None:
        lo.data.energy = energy
        lo.data.keyframe_insert("energy", frame=F(f))
    if color is not None:
        lo.data.color = color
        lo.data.keyframe_insert("color", frame=F(f))


# ------------------------------------------------------------------ pick up / put down (Child Of with keyed influence)
def pickup(ctx, prop, c, bone, f):
    """From local frame f the prop follows c's bone, starting exactly where it is (no pop).
    Call after the character's animation for frame f has been keyed."""
    sc = ctx.sc
    sc.frame_set(F(f))
    con = prop.constraints.new("CHILD_OF")
    con.target = c.arm
    con.subtarget = bone
    pb = c.arm.pose.bones[bone]
    con.inverse_matrix = (c.arm.matrix_world @ pb.matrix).inverted()
    con.influence = 0.0
    con.keyframe_insert("influence", frame=F(f) - 1)
    con.influence = 1.0
    con.keyframe_insert("influence", frame=F(f))
    for fr in (F(f) - 1, F(f)):
        set_interp_at(con, "influence", fr, "CONSTANT")
    prop["_con"] = con.name
    return con


def drop(ctx, prop, f):
    """Release at local frame f: the prop freezes at its current world transform."""
    sc = ctx.sc
    sc.frame_set(F(f))
    mw = prop.matrix_world.copy()
    con = prop.constraints[prop["_con"]]
    con.influence = 1.0
    con.keyframe_insert("influence", frame=F(f) - 1)
    con.influence = 0.0
    con.keyframe_insert("influence", frame=F(f))
    for fr in (F(f) - 1, F(f)):
        set_interp_at(con, "influence", fr, "CONSTANT")
    if prop.parent:
        mw = (prop.parent.matrix_world @ prop.matrix_parent_inverse).inverted() @ mw
    loc, rot, scl = mw.decompose()
    prop.rotation_mode = "XYZ"
    prop.location = loc
    prop.rotation_euler = rot.to_euler()
    prop.keyframe_insert("location", frame=F(f))
    prop.keyframe_insert("rotation_euler", frame=F(f))
    set_interp_at(prop, "location", F(f), "CONSTANT")


def static_key(o, f):
    """Key an object's current transform (so later drops don't drift its earlier placement)."""
    o.keyframe_insert("location", frame=F(f))
    o.keyframe_insert("rotation_euler", frame=F(f))


def xbot_glow(c, strength=8):
    """Yellow eye-glow light riding on X-BOT's body (lights nearby faces)."""
    lt = point("xbot_glow", (0, -0.35, 0.67), energy=strength, color=(1.0, 0.65, 0.15), radius=0.08)
    bind(lt, c.arm, "body")
    return lt


def carry(ctx, prop, c, side, f, offset=(0, -0.06, -0.02)):
    """Place prop at c's posed hand at local frame f and make it follow from there (droppable)."""
    ctx.sc.frame_set(F(f))
    b = c.arm.pose.bones[f"hand.{side}"]
    p = c.arm.matrix_world @ ((b.head + b.tail) / 2) + Vector(offset)
    prop.location = p
    static_key(prop, f)
    bpy.context.view_layer.update()
    pickup(ctx, prop, c, f"hand.{side}", f)
    return prop
