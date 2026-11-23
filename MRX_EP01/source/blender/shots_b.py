"""Scenes 05-09: disappointment, the secret, X-BOT, lesson, punchline."""
import math
from mathutils import Vector
from shotkit import *  # noqa
import envs as E

SHOTS = {}


def reg(f):
    SHOTS[f.__name__] = f
    return f


# ------------------------------------------------------------------ bedroom desk set-up
CHAIR = (0.9, -0.42, 0)
MDH = (0.9, -0.42, 0.97)          # MR X head while seated
DESK_Z = 0.44
BOX_AT = (0.9, 0.02, DESK_Z)


def desk_scene(sid):
    ctx = setup(sid, "bedroom", ["MRX"])
    m = ctx.chars["MRX"]
    place(m, 0, CHAIR, 180)
    sit(m, 0)
    expr(m, 0, "neutral")
    blinks(m, 0, ctx.n, seed=hash(sid) % 50)
    life(m, 0.8, 3)
    H = ctx.H
    light_key(H["top"], 0, energy=25)
    light_key(H["fill"], 0, energy=30)
    return ctx, m


def desk_arms(m, f, reach=40):
    arm(m, "L", f, fwd=reach, out=-6, elbow=50)
    arm(m, "R", f, fwd=reach, out=-6, elbow=50)


def front_cam(ctx, f0, f1, d0=1.25, d1=1.05, lens=35, z=0.82, look=MDH, x=0.9):
    z = min(z, 0.84)          # stay below the wall shelf (z~0.95) that sits between desk and camera
    ctx.cam(lens=lens, fstop=2.4)
    ctx.ck(f0, (x + 0.08, look[1] + d0, z), look, focus=(look[0], look[1] + 0.33, look[2]))
    ctx.ck(f1, (x + 0.04, look[1] + d1, z), look, focus=(look[0], look[1] + 0.33, look[2]))


def mahkota(name="mk_bottle", loc=(0, 0, 0)):
    return E.perfume_bottle(name, loc, s=1.15, liquid=(0.95, 0.5, 0.1), cap="gold")


# =================================================================== SCENE 05
@reg
def sh05a(ctx=None):
    ctx, m = desk_scene("sh05a")
    bx = E.perfume_box("buy_box", (0, 0, 0), s=1.1)
    # carries the box in with both hands, sets it down carefully, little satisfied wiggle
    for f, (fw, el) in ((0, (60, 50)), (20, (66, 40)), (38, (70, 10)), (44, (60, 30))):
        arm(m, "R", f, fwd=fw, out=-28, elbow=el, hand=(fw + el, 0, 0))
        arm(m, "L", f, fwd=fw, out=-28, elbow=el)
    desk_arms(m, 60, 30)
    head(m, 0, nod=14)
    head(m, 40, nod=20)
    expr(m, 46, "happy")
    for i, f in enumerate(range(48, 75, 6)):
        chest(m, f, turn=(6 if i % 2 else -6), tilt=(4 if i % 2 else -4))
    carry(ctx, bx, m, "R", 0, offset=(0.1, -0.1, -0.1))
    drop(ctx, bx, 40)
    ctx.cam(lens=30, fstop=3)
    ctx.ck(0, (-0.2, -1.75, 1.3), (0.85, -0.1, 0.62), focus=(0.9, -0.3, 0.7))
    ctx.ck(75, (0.0, -1.5, 1.2), (0.85, -0.1, 0.62), focus=(0.9, -0.3, 0.7))
    return ctx


@reg
def sh05b(ctx=None):
    ctx, m = desk_scene("sh05b")
    bx = E.perfume_box("desk_box", BOX_AT, s=1.1)
    lid = bpy.data.objects[bx["lid"]]
    bt = mahkota("mk_bottle", (BOX_AT[0], BOX_AT[1], DESK_Z + 0.02))
    cap = bpy.data.objects[bt["cap"]]
    for o in (lid, bt, cap):
        static_key(o, 0)
    desk_arms(m, 0, 35)
    # R fist to lid, lift it off
    arm(m, "R", 12, fwd=62, out=-14, elbow=30, hand=(90, 0, 0))
    arm(m, "R", 30, fwd=95, out=-14, elbow=40, hand=(130, 0, 0))
    arm(m, "R", 38, fwd=70, out=20, elbow=40, hand=(110, 0, 0))
    pickup(ctx, lid, m, "hand.R", 12)
    drop(ctx, lid, 38)
    # both fists in, lift the bottle out slowly (reverent)
    arm(m, "L", 40, fwd=58, out=-16, elbow=30, hand=(88, 0, 0))
    arm(m, "L", 66, fwd=88, out=-16, elbow=50, hand=(138, 0, 0))
    arm(m, "R", 46, fwd=58, out=-6, elbow=40)
    pickup(ctx, bt, m, "hand.L", 42)
    # R pops the cap
    arm(m, "R", 72, fwd=92, out=-20, elbow=55, hand=(147, 0, 0))
    arm(m, "R", 86, fwd=110, out=-6, elbow=40, hand=(150, 0, 0))
    pickup(ctx, cap, m, "hand.R", 76)
    head(m, 0, nod=22)
    head(m, 66, nod=6)
    gaze(m, 0, 0, -20)
    gaze(m, 66, 0, -4)
    expr(m, 60, "excited")
    sparkle(m, 64, True)
    ctx.cam(lens=40, fstop=2.0)
    ctx.ck(0, (0.98, 0.72, 0.72), (0.9, 0.02, 0.56), focus=(0.9, 0.02, 0.56))
    ctx.ck(45, (0.95, 0.62, 0.74), (0.9, 0.0, 0.62), focus=(0.9, 0.0, 0.6))
    ctx.ck(90, (0.92, 0.52, 0.82), (0.88, -0.15, 0.75), focus=(0.88, -0.15, 0.75))
    return ctx


def mrx_spray_setup(ctx, m, bottle_side="R"):
    bt = hold(m, bottle_side, mahkota("mk_bottle"), offset=(0, -0.06, 0.03))
    return bt


@reg
def sh05c(ctx=None):
    ctx, m = desk_scene("sh05c")
    bt = mrx_spray_setup(ctx, m)
    # L wrist up (forearm raised), bottle aimed at it
    arm(m, "L", 0, fwd=40, out=-6, elbow=50)
    arm(m, "L", 10, fwd=55, out=-30, elbow=95, hand=(0, 0, 0))
    arm(m, "R", 0, fwd=60, out=-6, elbow=40, hand=(100, 0, 0))
    arm(m, "R", 12, fwd=62, out=-30, elbow=40, hand=(100, 0, 60))
    arm(m, "R", 15, fwd=60, out=-30, elbow=36, hand=(100, 0, 60))   # PSSHT recoil
    arm(m, "R", 22, fwd=55, out=-10, elbow=40, hand=(95, 0, 20))
    # sniff: brings wrist to face, head dips, little shoulder lift
    arm(m, "L", 30, fwd=70, out=-40, elbow=130)
    head(m, 30, nod=16, turn=10)
    hips(m, 33, loc=(0, 0, -0.05 + 0.02))
    hips(m, 38, loc=(0, 0, -0.05))
    expr(m, 26, "happy")
    expr(m, 34, "closed")
    expr(m, 46, "happy")
    # spray mist burst
    mist = []
    mm = mat("mist", (1, 1, 1), rough=0.2)
    mm.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.25
    ctx.sc.frame_set(F(15))
    nozzle = bt.matrix_world.translation + Vector((0, 0, 0.17))
    import random
    rnd = random.Random(5)
    for i in range(26):
        s = sphere(f"mist{i}", nozzle, 0.006, m=mm, seg=8, rings=4)
        d = Vector((rnd.uniform(-0.05, 0.05), rnd.uniform(-0.05, 0.05), rnd.uniform(-0.02, 0.05)))
        to = Vector((-0.1 + 0.9, -0.35, 0.72)) if False else nozzle + Vector((0.16, 0.0, -0.06)) + d
        obj_key(s, F(14), loc=nozzle, scale=0.01)
        obj_key(s, F(15), loc=nozzle, scale=1.0)
        obj_key(s, F(15 + rnd.randint(6, 12)), loc=to, scale=3.5)
        obj_key(s, F(32), loc=to + Vector((0, 0, 0.04)), scale=0.01)
    front_cam(ctx, 0, 60, d0=1.2, d1=1.0, z=0.86, look=(0.9, -0.42, 0.85))
    return ctx


@reg
def sh05d(ctx=None):
    ctx, m = desk_scene("sh05d")
    st, ln = ctx.line("s05_mrx_eh")
    arm(m, "L", 0, fwd=70, out=-40, elbow=130)
    arm(m, "R", 0, fwd=40, out=-6, elbow=50)
    head(m, 0, nod=12, turn=8)
    expr(m, 0, "closed")
    # freeze... eyes open slowly, narrow
    expr(m, st - 2, "closed")
    expr(m, st + 4, "neutral")
    expr(m, st + 14, "suspicious")
    head(m, st + 6, nod=0, tilt=-10)
    gaze(m, st + 6, 0, 0)
    gaze(m, st + 18, 14, -8)
    # sniff 2 (f40) and sniff 3 (f65) — progressively more desperate
    for f0, dip in ((40, 14), (65, 20)):
        head(m, f0 - 6, nod=0, tilt=-10)
        head(m, f0, nod=dip, turn=10)
        hips(m, f0, loc=(0, 0, -0.03))
        hips(m, f0 + 4, loc=(0, 0, -0.05))
        head(m, f0 + 10, nod=2, tilt=-12)
    expr(m, 66, "squint")
    talk_bob(m, ctx, "s05_mrx_eh", amp=1.2)
    front_cam(ctx, 0, 90, d0=1.05, d1=0.85, z=0.95, look=MDH)
    return ctx


@reg
def sh05e(ctx=None):
    ctx, m = desk_scene("sh05e")
    H = ctx.H
    dupe = H["dupe"]
    static_key(dupe, 0)
    gaze(m, 0, 0, 0)
    gaze(m, 8, -14, 22)          # eyes find the old bottle (up, to his left)
    head(m, 14, nod=-18, turn=18, interp="BACK")
    expr(m, 10, "suspicious")
    expr(m, 16, "wide")
    # L hand reaches up to the shelf, grabs, brings it down
    arm(m, "L", 0, fwd=40, out=-6, elbow=50)
    arm(m, "L", 22, fwd=10, out=-6, elbow=20)
    arm(m, "L", 36, fwd=150, out=-12, elbow=10, hand=(160, 0, 0))
    pickup(ctx, dupe, m, "hand.L", 38)
    arm(m, "L", 54, fwd=70, out=-30, elbow=55, hand=(125, 0, 0))
    arm(m, "L", 72, fwd=60, out=-34, elbow=40, hand=(100, 0, -50))
    # R wrist presented, spray at 75
    arm(m, "R", 50, fwd=55, out=-30, elbow=95)
    arm(m, "L", 75, fwd=58, out=-30, elbow=36, hand=(100, 0, -50))
    head(m, 60, nod=14, turn=-6)
    expr(m, 60, "squint")
    ctx.cam(lens=28, fstop=2.8)
    ctx.ck(0, (1.6, -1.0, 1.05), (0.82, -0.1, 0.92), focus=(0.85, -0.3, 0.95))
    ctx.ck(40, (1.5, -0.95, 1.08), (0.78, 0.1, 0.98), focus=(0.74, 0.4, 1.0))
    ctx.ck(90, (1.45, -1.05, 1.0), (0.85, -0.25, 0.85), focus=(0.88, -0.4, 0.88))
    return ctx


@reg
def sh05f(ctx=None):
    ctx, m = desk_scene("sh05f")
    arm(m, "L", 0, fwd=66, out=-38, elbow=125)
    arm(m, "R", 0, fwd=66, out=-38, elbow=125)
    switches = [0, 20, 35, 47, 56, 63, 69, 74]
    expr(m, 0, "squint")
    for i, f in enumerate(switches):
        side = 1 if i % 2 == 0 else -1
        head(m, f, nod=14, turn=16 * side)
        hips(m, f, loc=(0, 0, -0.04))
        if i < len(switches) - 1:
            mid = (f + switches[i + 1]) / 2
            head(m, mid, nod=6, turn=4 * side)
            hips(m, mid, loc=(0, 0, -0.05))
        expr(m, f, "squint" if i < 5 else "suspicious")
    gaze(m, 0, 10, -10)
    gaze(m, 40, -10, -10)
    front_cam(ctx, 0, 75, d0=1.0, d1=0.82, z=0.95, look=MDH)
    return ctx


@reg
def sh05g(ctx=None):
    ctx, m = desk_scene("sh05g")
    st, ln = ctx.line("s05_mrx_bau")
    arm(m, "L", 0, fwd=66, out=-38, elbow=125)
    arm(m, "R", 0, fwd=66, out=-38, elbow=125)
    expr(m, 0, "suspicious")
    head(m, 0, nod=10)
    # realization: freeze, then SNAP wide + recoil, arms fly out
    expr(m, st - 2, "suspicious")
    expr(m, st + 1, "shock")
    eye_size(m, st, 1.0)
    eye_size(m, st + 3, 1.45, interp="BACK")
    eye_size(m, st + 30, 1.3)
    head(m, st + 2, nod=-18, tilt=-6, interp="BACK")
    chest(m, st + 2, lean=-14)
    arm(m, "L", st + 3, fwd=70, out=70, elbow=40, interp="BACK")
    arm(m, "R", st + 3, fwd=70, out=70, elbow=40, interp="BACK")
    hips(m, st + 3, loc=(0, 0, 0.03))
    hips(m, st + 10, loc=(0, 0, -0.05))
    head(m, st + 36, nod=-8, tilt=10)
    arm(m, "L", st + 40, fwd=80, out=20, elbow=110)   # points at the wrists, outraged
    arm(m, "R", st + 40, fwd=80, out=20, elbow=110)
    talk_bob(m, ctx, "s05_mrx_bau", amp=1.6)
    H = ctx.H
    flash = area("realize_rim", (0.9, 0.6, 1.4), MDH, energy=0, color=(1.0, 0.85, 0.4), size=0.5)
    light_key(flash, st, energy=0)
    light_key(flash, st + 2, energy=400)
    light_key(flash, st + 14, energy=60)
    front_cam(ctx, 0, 80, d0=0.95, d1=0.75, z=0.97, look=MDH)
    ctx.ck(st, (0.96, -0.42 + 0.85, 0.83), MDH, focus=(0.9, -0.09, 0.97), interp="CONSTANT")
    ctx.ck(st + 1, (0.95, -0.42 + 0.62, 0.83), MDH, focus=(0.9, -0.09, 0.97), interp="BACK")
    ctx.ck(80, (0.94, -0.42 + 0.68, 0.83), MDH, focus=(0.9, -0.09, 0.97))
    return ctx


@reg
def sh05h(ctx=None):
    ctx, m = desk_scene("sh05h")
    bx = E.perfume_box("desk_box", (0.78, 0.02, DESK_Z), s=1.1)
    static_key(bx, 0)
    st, ln = ctx.line("s05_mrx_habis")
    H = ctx.H
    expr(m, 0, "furious")
    eye_size(m, 0, 1.2)
    head(m, 0, nod=-10)
    # anger build: shaking, arms pumping on beats
    for i, f in enumerate(range(st, st + 60, 3)):
        hips(m, f, loc=((0.006 if i % 2 else -0.006), 0, -0.05))
    arm(m, "L", st, fwd=60, out=30, elbow=110)
    arm(m, "R", st, fwd=60, out=30, elbow=110)
    for f in (st + 12, st + 30, st + 48):
        arm(m, "L", f, fwd=95, out=30, elbow=90)
        arm(m, "R", f, fwd=95, out=30, elbow=90)
        arm(m, "L", f + 5, fwd=60, out=30, elbow=110)
        arm(m, "R", f + 5, fwd=60, out=30, elbow=110)
    # grabs the box ("KOTAK?!"), raises it high, SLAMS it at 98
    arm(m, "L", 66, fwd=52, out=-6, elbow=20, hand=(72, 0, 0))
    pickup(ctx, bx, m, "hand.L", 68)
    arm(m, "L", 86, fwd=160, out=-10, elbow=20, hand=(180, 0, 0))
    arm(m, "R", 86, fwd=150, out=-20, elbow=30)
    arm(m, "L", 98, fwd=55, out=-6, elbow=18, hand=(73, 0, 0), interp="LINEAR")
    arm(m, "R", 98, fwd=60, out=-10, elbow=20)
    drop(ctx, bx, 98)
    head(m, 86, nod=-22)
    head(m, 98, nod=16, interp="LINEAR")
    head(m, 104, nod=8)
    expr(m, 86, "furious")
    eye_size(m, 86, 1.35)
    talk_bob(m, ctx, "s05_mrx_habis", amp=2.0)
    # stylized anger lighting: room goes red
    red = area("anger_red", (0.9, -1.4, 1.6), MDH, energy=0, color=(1.0, 0.08, 0.05), size=1.5)
    light_key(red, st - 2, energy=0)
    light_key(red, st + 4, energy=320)
    light_key(H["moon"], st - 2, energy=220)
    light_key(H["moon"], st + 4, energy=60)
    light_key(H["warm"], st + 4, energy=40)
    ctx.cam(lens=40, fstop=2.2)
    ctx.ck(0, (0.93, -0.42 + 0.62, 0.83), MDH, focus=(0.9, -0.09, 0.97))
    ctx.ck(st + 2, (0.93, -0.42 + 0.55, 0.84), MDH, focus=(0.9, -0.09, 0.97), interp="CONSTANT")
    ctx.ck(st + 3, (1.05, 0.9, 0.95), (0.88, -0.42, 0.85), focus=(0.9, -0.15, 0.9), lens=32)
    ctx.ck(110, (1.0, 0.8, 0.95), (0.88, -0.42, 0.82), focus=(0.9, -0.15, 0.9))
    return ctx


# =================================================================== SCENE 06 — STOREROOM
UPOS = (0, 0.8, 0)        # uncle behind the table, facing the front (-Y)
UHS = (0, 0.8, 1.06)


def store_scene(sid, chars=("UNCLE",)):
    ctx = setup(sid, "storeroom", list(chars))
    u = ctx.chars.get("UNCLE")
    if u:
        place(u, 0, UPOS, 0)
        expr(u, 0, "smug")
        smile(u, 0, 0.6)
        blinks(u, 0, ctx.n, seed=7)
        life(u, 1.0, 5)
    return ctx, u


@reg
def sh06a(ctx=None):
    ctx, u = store_scene("sh06a")
    H = ctx.H
    money = hold(u, "R", E.money_stack("cash", n=8, s=1.0), offset=(0, -0.07, 0.0))
    obj_key(H["door"], F(0), rot=(0, 0, 0))
    obj_key(H["door"], F(4), rot=(0, 0, 0))
    obj_key(H["door"], F(28), rot=(0, 0, -100))
    light_key(H["doorlight"], 0, energy=0)
    light_key(H["doorlight"], 26, energy=260)
    place(u, 0, (-2.4, -0.6, 0), 90)
    u.walk(F(14), F(46), (-2.4, -0.6, 0), (-0.9, -0.35, 0), step_frames=9, bounce=0.02)
    u.walk(F(46), F(74), (-0.9, -0.35, 0), (0.0, 0.75, 0), step_frames=9, bounce=0.02)
    arm(u, "R", 0, fwd=40, out=-10, elbow=70, hand=(110, 0, 0))
    for f in range(14, 75, 9):
        arm(u, "R", f, fwd=40, out=-10, elbow=70, hand=(110, 0, 0))
    gaze(u, 0, 10, 0)
    gaze(u, 30, -12, -6)
    expr(u, 0, "smug")
    smile(u, 30, 0.8)
    ctx.cam(lens=34, fstop=3.0)
    ctx.ck(0, (1.2, -2.3, 1.15), (-1.5, -0.6, 0.85), focus=(-1.7, -0.6, 0.9))
    ctx.ck(46, (1.1, -2.2, 1.15), (-0.8, -0.3, 0.85), focus=(-0.9, -0.35, 0.9))
    ctx.ck(75, (0.9, -2.0, 1.2), (-0.1, 0.5, 0.85), focus=(0, 0.6, 0.9))
    return ctx


@reg
def sh06b(ctx=None):
    ctx, u = store_scene("sh06b")
    E.money_stack("cash_table", (0.18, 0.4, 0.525), n=12)
    note = hold(u, "L", E.note_single("count_note", (0, 0, 0), s=1.0, rot=(0, math.radians(90), 0)),
                offset=(0, -0.06, 0.02))
    # counting motion: L hand holds stack, R thumb flicks — alternate every 4 frames
    for i, f in enumerate(range(0, 88, 4)):
        arm(u, "L", f, fwd=62, out=-22, elbow=40, hand=(100, 0, (8 if i % 2 else -8)))
        arm(u, "R", f, fwd=60, out=-26, elbow=(46 if i % 2 else 36))
    head(u, 0, nod=22)
    gaze(u, 0, 0, -24)
    st, ln = ctx.line("s06_unc_hehe")
    lipsync(u, ctx, "s06_unc_hehe", smile_v=1.0)
    for i, f in enumerate(range(st, st + ln, 5)):     # giggle shoulders
        chest(u, f, lean=(3 if i % 2 else -1))
    st2, ln2 = ctx.line("s06_unc_konon")
    head(u, st2 - 4, nod=4, tilt=-8)
    gaze(u, st2 - 2, 4, 2)
    brows(u, st2, 2.0, -0.5, angle=6)
    expr(u, st2, "smug")
    lipsync(u, ctx, "s06_unc_konon", smile_v=1.0)
    ctx.cam(lens=35, fstop=2.0)
    ctx.ck(0, (0.18, -0.2, 0.78), (0.02, 0.55, 0.62), focus=(0.02, 0.55, 0.65))
    ctx.ck(st2 - 6, (0.15, -0.25, 0.85), (0.02, 0.6, 0.70), focus=(0.02, 0.55, 0.7))
    ctx.ck(st2 + 6, (0.1, -0.3, 1.0), UHS, focus=(0, 0.6, 1.05))
    ctx.ck(88, (0.08, -0.25, 1.02), UHS, focus=(0, 0.6, 1.05))
    return ctx


@reg
def sh06c(ctx=None):
    ctx, u = store_scene("sh06c")
    H = ctx.H
    st, ln = ctx.line("s06_unc_padahal")
    expr(u, 0, "smug")
    smile(u, 0, 1.0)
    head(u, 0, nod=-4)
    arm(u, "L", st + 10, fwd=30, out=60, elbow=30)       # gestures back at the drums
    arm(u, "L", st + 30, fwd=20, out=80, elbow=10, interp="BACK")
    chest(u, st + 30, turn=14)
    head(u, st + 34, turn=20, nod=-6)
    # turns and walks to the drum, taps it twice
    u.walk(F(60), F(86), UPOS, (0.32, 1.0, 0), step_frames=9, bounce=0.015)
    place(u, 88, (0.32, 1.0, 0), 160)
    arm(u, "R", 92, fwd=80, out=-10, elbow=40)
    arm(u, "R", 100, fwd=95, out=-10, elbow=20)
    arm(u, "R", 104, fwd=80, out=-10, elbow=40)
    arm(u, "R", 108, fwd=95, out=-10, elbow=20)
    arm(u, "R", 116, fwd=60, out=-6, elbow=50)
    head(u, 96, turn=-40, nod=-6)
    brows(u, 96, 2.0, 2.0)
    lipsync(u, ctx, "s06_unc_padahal", smile_v=1.0)
    # reveal light: drums get lit as the camera pulls out
    light_key(H["drumlight"], 0, energy=10)
    light_key(H["drumlight"], 40, energy=10)
    light_key(H["drumlight"], 70, energy=160)
    ctx.cam(lens=35, fstop=2.0)
    ctx.ck(0, (0.12, 0.08, 1.06), UHS, focus=(0, 0.6, 1.05))
    ctx.ck(30, (0.12, 0.0, 1.06), UHS, focus=(0, 0.6, 1.05))
    ctx.ck(90, (1.05, -2.05, 1.65), (0.25, 1.0, 0.7), focus=(0.2, 1.1, 0.7), lens=24)
    ctx.ck(130, (1.0, -1.95, 1.6), (0.3, 1.1, 0.7), focus=(0.35, 1.2, 0.6), lens=24)
    return ctx


@reg
def sh06d(ctx=None):
    """6-cut montage (18 frames each), stylized production story — not a recipe."""
    ctx, u = store_scene("sh06d", chars=())
    amber = E.liquid_mat("amber_conc", (0.95, 0.5, 0.08))
    stream_m = mat("stream", (0.95, 0.55, 0.1), rough=0.05, emit=(1.0, 0.5, 0.1), emit_str=0.6)
    # d2: measuring jug filling from a pour stream
    jug = cyl("jug", (-0.45, 0.08, 0.525 + 0.07), 0.05, 0.14, m=E.glass_mat("glass"))
    jl = cyl("jug_liq", (-0.45, 0.08, 0.53), 0.044, 0.01, m=amber)
    jl.data.transform(__import__("mathutils").Matrix.Translation((0, 0, 0.005)))
    st1 = cyl("stream1", (-0.45, 0.08, 0.75), 0.006, 0.4, m=stream_m)
    obj_key(jl, F(18), scale=(1, 1, 1))
    obj_key(jl, F(35), scale=(1, 1, 11))
    # d3: funnel into bottle row
    fn = cyl("funnel2", (0.0, 0.08, 0.70), 0.035, 0.05, m=mat("funnelm", (0.6, 0.62, 0.65), rough=0.25, metal=0.9))
    b3 = E.perfume_bottle("fill_a", (0.0, 0.08, 0.525), s=1.15, liquid=(0.95, 0.5, 0.1), cap="gold")
    bpy.data.objects[b3["cap"]].hide_render = True
    st2 = cyl("stream2", (0.0, 0.08, 0.8), 0.004, 0.2, m=stream_m)
    # d4: bottle fill macro: liquid level rising
    b4 = E.perfume_bottle("fill_b", (0.32, 0.08, 0.525), s=1.15, liquid=(0.95, 0.5, 0.1), cap="gold")
    lq = bpy.data.objects["fill_b_liq"]
    bpy.data.objects[b4["cap"]].hide_render = True
    hh = 0.085 * 1.15
    lq.data.transform(__import__("mathutils").Matrix.Translation((0, 0, hh / 2)))
    lq.location.z -= hh / 2
    obj_key(lq, F(54), scale=(1, 1, 0.05))
    obj_key(lq, F(71), scale=(1, 1, 1))
    # d5: box closing
    bx = E.perfume_box("pack_box", (0.52, 0.06, 0.525), s=1.1)
    lid = bpy.data.objects[bx["lid"]]
    obj_key(lid, F(72), loc=(0, 0, 0.19 * 1.1 + 0.10), rot=(-30, 0, 0))
    obj_key(lid, F(84), loc=(0, 0, 0.19 * 1.1), rot=(0, 0, 0))
    # d6: finished hero on plinth with spotlight
    cyl("hero_plinth", (-0.22, 0.12, 0.56), 0.08, 0.07, m=mat("plinthblk", (0.01, 0.01, 0.012), rough=0.1, coat=1))
    hero = E.perfume_bottle("hero_final", (-0.22, 0.12, 0.595), s=1.2, liquid=(0.95, 0.5, 0.1), cap="gold")
    hs = spot("hero_spot", (-0.22, -0.3, 1.3), (-0.22, 0.12, 0.65), energy=0, color=(1.0, 0.8, 0.5), angle=18)
    light_key(hs, 89, energy=0)
    light_key(hs, 90, energy=180)
    ctx.cam(lens=40, fstop=2.0)
    cuts = [
        (0, (-0.9, 0.65, 0.55), (-0.9, 1.3, 0.45), (-0.9, 1.18, 0.45), (-0.82, 0.75, 0.5)),     # drum label
        (18, (-0.25, -0.25, 0.68), (-0.45, 0.08, 0.62), (-0.45, 0.08, 0.6), (-0.3, -0.18, 0.66)),   # concentrate pour
        (36, (0.16, -0.25, 0.72), (0.0, 0.08, 0.66), (0.0, 0.08, 0.66), (0.08, -0.22, 0.75)),        # funnel
        (54, (0.40, -0.18, 0.60), (0.32, 0.08, 0.59), (0.32, 0.08, 0.59), (0.36, -0.15, 0.62)),       # fill macro
        (72, (0.66, -0.3, 0.84), (0.52, 0.06, 0.66), (0.52, 0.06, 0.66), (0.6, -0.26, 0.8)),          # packaging
        (90, (0.05, -0.35, 0.72), (-0.22, 0.12, 0.69), (-0.22, 0.12, 0.69), (-0.42, -0.32, 0.70)),    # finished
    ]
    for f0, p0, look, foc, p1 in cuts:
        ctx.ck(f0, p0, look, focus=foc)
        ctx.ck(f0 + 17, p1, look, focus=foc)
        ctx.hold_cut(f0 + 17)
    return ctx


@reg
def sh06e(ctx=None):
    ctx, u = store_scene("sh06e")
    bt = hold(u, "R", mahkota("pretty_bottle"), offset=(0.0, -0.07, 0.03))
    st, ln = ctx.line("s06_unc_tukar")
    arm(u, "R", 0, fwd=40, out=-10, elbow=50, hand=(90, 0, 0))
    arm(u, "R", st + 10, fwd=90, out=-20, elbow=60, hand=(150, 0, 0), interp="BACK")
    arm(u, "R", st + 40, fwd=92, out=-22, elbow=58, hand=(150, 0, 25))
    head(u, st + 10, nod=-4, tilt=8, turn=-10)
    gaze(u, st + 10, -10, 4)
    expr(u, st + 10, "happy")
    brows(u, st + 10, 1.8, 1.8)
    lipsync(u, ctx, "s06_unc_tukar", smile_v=1.0)
    ctx.cam(lens=45, fstop=2.0)
    ctx.ck(0, (0.25, -0.75, 1.02), (0, 0.8, 0.98), focus=(-0.02, 0.6, 1.0))
    ctx.ck(60, (0.2, -0.6, 1.0), (0, 0.8, 1.0), focus=(-0.02, 0.6, 1.0))
    return ctx


@reg
def sh06f(ctx=None):
    ctx, u = store_scene("sh06f")
    bt = hold(u, "R", mahkota("pretty_bottle"), offset=(0.0, -0.07, 0.03))
    bx = E.perfume_box("open_box", (-0.12, 0.38, 0.525), s=1.1)
    bpy.data.objects[bx["lid"]].hide_render = True
    st, ln = ctx.line("s06_unc_kotak")
    arm(u, "R", 0, fwd=90, out=-20, elbow=60, hand=(150, 0, 0))
    arm(u, "R", 20, fwd=70, out=-25, elbow=40, hand=(110, 0, 0))
    arm(u, "R", 38, fwd=48, out=-22, elbow=36, hand=(84, 0, 0))
    drop(ctx, bt, 38) if False else None
    arm(u, "L", 30, fwd=50, out=-15, elbow=40)
    head(u, 10, nod=18)
    gaze(u, 10, 0, -18)
    smile(u, 0, 1.0)
    lipsync(u, ctx, "s06_unc_kotak", smile_v=1.0)
    ctx.cam(lens=32, fstop=2.4)
    ctx.ck(0, (0.35, -0.35, 1.2), (-0.08, 0.45, 0.7), focus=(-0.1, 0.4, 0.68))
    ctx.ck(55, (0.3, -0.3, 1.15), (-0.1, 0.42, 0.66), focus=(-0.12, 0.38, 0.66))
    return ctx


@reg
def sh06g(ctx=None):
    ctx, u = store_scene("sh06g")
    H = ctx.H
    st, ln = ctx.line("s06_unc_ingat")
    arm(u, "L", st, fwd=30, out=10, elbow=40)
    arm(u, "L", st + 16, fwd=100, out=10, elbow=90)     # points at temple: "dia ingat..."
    head(u, st + 16, nod=-4, tilt=10)
    brows(u, st + 16, 2.2, 0.4, angle=4)
    expr(u, st + 10, "smug")
    lipsync(u, ctx, "s06_unc_ingat", smile_v=1.0)
    # the laugh: quiet chuckle -> smug -> full theatrical HAHAHA (head back, belly shake)
    h0 = 84
    arm(u, "L", h0 - 6, fwd=30, out=10, elbow=40)
    arm(u, "L", h0 + 2, fwd=40, out=-30, elbow=110)
    arm(u, "R", h0 + 2, fwd=40, out=-30, elbow=110)
    head(u, h0, nod=-6)
    head(u, h0 + 8, nod=-28, interp="BACK")
    expr(u, h0 + 6, "closed")
    brows(u, h0 + 6, 2.6, 2.6, angle=-4)
    for i, f in enumerate(range(h0 + 6, 150, 3)):
        chest(u, f, lean=(-10 if i % 2 else -4), tilt=(3 if i % 2 else -3))
        smile(u, f, 1.0, 0.95 if i % 2 else 0.55)
    expr(u, 132, "smug")
    # lighting turns theatrical
    light_key(H["bulb"], h0 - 2, energy=60)
    light_key(H["bulb"], h0 + 4, energy=12)
    under = area("villain_under", (0.1, 0.35, 0.3), UHS, energy=0, color=(1.0, 0.55, 0.15), size=0.4)
    light_key(under, h0 - 2, energy=0)
    light_key(under, h0 + 4, energy=160)
    light_key(H["rim"], h0 + 4, energy=380)
    gl = area("glint_light", (0.4, 0.0, 1.2), UHS, energy=0, color=(1.0, 0.8, 0.35), size=0.12)
    light_key(gl, 88, energy=0)
    light_key(gl, 92, energy=420)
    light_key(gl, 104, energy=0)
    ctx.cam(lens=28, fstop=2.4)
    ctx.ck(0, (0.2, 0.05, 0.85), UHS, focus=(0, 0.62, 1.05))
    ctx.ck(h0, (0.18, 0.15, 0.78), UHS, focus=(0, 0.62, 1.05))
    ctx.ck(h0 + 1, (0.14, 0.28, 0.66), (0, 0.8, 1.12), focus=(0, 0.62, 1.08), interp="BACK")
    ctx.ck(150, (0.12, 0.33, 0.66), (0, 0.8, 1.14), focus=(0, 0.62, 1.08))
    return ctx


# =================================================================== SCENES 07-09 — BEDROOM
MPOS = (-1.1, -0.85, 0)            # MR X standing spot, bed right behind him
MHH = (-1.1, -0.85, 1.0)
XPOS = (-0.2, -0.95, 0)            # X-BOT landing spot (screen right of MR X)
XH = (-0.2, -0.95, 0.82)
MRZ = 53                           # MR X faces X-BOT, cheated ~30 deg toward camera
XRZ = -66                          # X-BOT faces MR X, cheated ~30 deg toward camera


def fcam(pos, rz, dist, z, side=0):
    """Camera position in front of a character facing rz (deg), optionally orbiting by `side` deg."""
    a = math.radians(rz + side)
    return (pos[0] + math.sin(a) * dist, pos[1] - math.cos(a) * dist, z)


def room_scene(sid, chars=("MRX", "XBOT"), mood="night"):
    ctx = setup(sid, "bedroom", list(chars))
    H = ctx.H
    light_key(H["top"], 0, energy=20)
    light_key(H["fill"], 0, energy=35)
    light_key(H["moon"], 0, energy=300)
    m = ctx.chars.get("MRX")
    x = ctx.chars.get("XBOT")
    if m:
        expr(m, 0, "neutral")
        blinks(m, 0, ctx.n, seed=11)
        life(m, 0.8, 9)
    if x:
        place(x, 0, XPOS, XRZ)
        xeyes(x, 0, 1.0, 0.6, 1.0)
        xbot_glow(x)
        life(x, 0.6, 4)
    return ctx, m, x


def mrx_hug_box(ctx, m):
    bx = hold(m, "R", E.perfume_box("hug_box", s=1.1), offset=(0.12, -0.09, 0.08))
    return bx


def hug_pose(m, f, interp=None):
    arm(m, "R", f, fwd=70, out=-40, elbow=70, hand=(130, 0, 0), interp=interp)
    arm(m, "L", f, fwd=70, out=-40, elbow=80, interp=interp)


def xbot_akimbo(x, f, interp=None):
    arm(x, "L", f, fwd=-10, out=40, elbow=100, interp=interp)
    arm(x, "R", f, fwd=-10, out=40, elbow=100, interp=interp)


@reg
def sh07a(ctx=None):
    ctx, m, x = room_scene("sh07a", ("MRX",))
    bx = mrx_hug_box(ctx, m)
    place(m, 0, (-1.1, -0.78, 0), 0)
    sit_floor(m, 0)
    hug_pose(m, 0)
    expr(m, 0, "sad")
    head(m, 0, nod=24, tilt=8)
    gaze(m, 0, 0, -16)
    # one long deflated sigh
    chest(m, 20, lean=4)
    chest(m, 36, lean=-4)
    head(m, 36, nod=12, tilt=6)
    chest(m, 56, lean=12)
    head(m, 60, nod=28, tilt=10)
    expr(m, 58, "closed")
    expr(m, 70, "sad")
    ctx.cam(lens=35, fstop=2.2)
    ctx.ck(0, (-0.55, -2.35, 0.62), (-1.1, -0.78, 0.48), focus=(-1.1, -0.95, 0.5))
    ctx.ck(75, (-0.7, -2.05, 0.6), (-1.1, -0.78, 0.5), focus=(-1.1, -0.95, 0.5))
    return ctx


@reg
def sh07b(ctx=None):
    ctx, m, x = room_scene("sh07b")
    bx = mrx_hug_box(ctx, m)
    place(m, 0, (-1.1, -0.78, 0), 0)
    sit_floor(m, 0)
    hug_pose(m, 0)
    expr(m, 0, "sad")
    head(m, 0, nod=24)
    expr(m, 6, "shock")
    head(m, 7, nod=-16, turn=24, interp="BACK")
    hips(m, 8, loc=(0, 0, -0.24))
    hips(m, 14, loc=(0, 0, -0.30))
    # X-BOT drop: gravity ease-in, impact squash, stretch, settle
    rz = XRZ
    place(x, 0, (XPOS[0], XPOS[1], 2.6), rz)
    place(x, 10, (XPOS[0], XPOS[1], 2.6), rz, interp="LINEAR")
    for f, z in ((16, 2.0), (20, 1.25), (23, 0.55), (25, 0.0)):
        place(x, f, (XPOS[0], XPOS[1], z), rz, interp="LINEAR")
    legs(x, 10, l=(20, 30), r=(10, 20))
    legs(x, 25, l=(0, 0), r=(0, 0), interp="LINEAR")
    pose(x.arm, "body", F(24), scale=(1, 1, 1), loc=(0, 0, 0))
    pose(x.arm, "body", F(26), scale=(1.22, 1.22, 0.72), loc=(0, 0, -0.08))
    legs(x, 26, l=(35, 70), r=(35, 70))
    pose(x.arm, "body", F(36), scale=(1.06, 1.06, 0.9), loc=(0, 0, -0.04))
    pose(x.arm, "body", F(42), scale=(0.92, 0.92, 1.12), loc=(0, 0, 0.03), interp="BACK")
    legs(x, 42, l=(0, 0), r=(0, 0))
    pose(x.arm, "body", F(50), scale=(1, 1, 1), loc=(0, 0, 0))
    arm(x, "L", 10, fwd=0, out=120, elbow=20)
    arm(x, "R", 10, fwd=0, out=120, elbow=20)
    arm(x, "L", 27, fwd=40, out=60, elbow=60)
    arm(x, "R", 27, fwd=40, out=60, elbow=60)
    xbot_akimbo(x, 46, interp="BACK")
    xeyes(x, 0, 0.6, 0.8, 1.0)
    xeyes(x, 40, 0.6, 0.8, 1.0)
    xeyes(x, 44, 1.1, 1.0, 1.25, interp="BACK")
    boom = point("boom_light", (XPOS[0], XPOS[1] + 0.2, 0.6), energy=0, color=(1.0, 0.75, 0.2), radius=0.3)
    light_key(boom, 3, energy=0)
    light_key(boom, 5, energy=900)
    light_key(boom, 14, energy=0)
    light_key(boom, 24, energy=0)
    light_key(boom, 26, energy=500)
    light_key(boom, 34, energy=0)
    ctx.cam(lens=24, fstop=3.0)
    c0 = fcam(XPOS, XRZ, 1.35, 0.22, 18)
    ctx.ck(0, c0, (XH[0], XH[1], 1.3), focus=XH)
    ctx.ck(25, c0, (XH[0], XH[1], 0.75), focus=XH)
    ctx.ck(60, fcam(XPOS, XRZ, 1.25, 0.24, 18), (XH[0], XH[1], 0.8), focus=XH)
    return ctx


def xbot_talk_shot(sid, lid, cam0, cam1=None, lens=32, gesture=None, mrx_visible=True):
    """cam0 = (dist, z, side_deg) relative to X-BOT's facing."""
    ctx, m, x = room_scene(sid, ("MRX", "XBOT") if mrx_visible else ("XBOT",))
    if m:
        bx = mrx_hug_box(ctx, m)
        place(m, 0, MPOS, MRZ)
        hug_pose(m, 0)
        expr(m, 0, "embarrassed")
    xbot_akimbo(x, 0)
    xeyes(x, 0, 1.0, 1.0, 1.15)
    talk_bob(x, ctx, lid, amp=1.8, bone="body")
    if gesture:
        gesture(ctx, x, m)
    d, z, sd = cam0
    ctx.cam(lens=lens, fstop=2.4)
    ctx.ck(0, fcam(XPOS, XRZ, d, z, sd), XH, focus=XH)
    ctx.ck(ctx.n, fcam(XPOS, XRZ, d * 0.9, z, sd), XH, focus=XH)
    return ctx


@reg
def sh07c(ctx=None):
    def g(ctx, x, m):
        st, ln = ctx.line("s07_xb_mrx")
        arm(x, "R", st, fwd=-10, out=40, elbow=100)
        arm(x, "R", st + 5, fwd=100, out=-10, elbow=0, interp="BACK")
        xpoint(x, st + 4, "R", True)
        pose(x.arm, "body", F(st + 5), rot=(8, 0, 0))
        pose(x.arm, "body", F(st + 30), rot=(4, 0, 0))
    return xbot_talk_shot("sh07c", "s07_xb_mrx", (1.15, 0.28, 10), lens=28,
                          gesture=g, mrx_visible=False)


@reg
def sh07d(ctx=None):
    ctx, m, x = room_scene("sh07d")
    bx = mrx_hug_box(ctx, m)
    st, ln = ctx.line("s07_mrx_woii")
    place(m, 0, (-1.1, -0.78, 0), 0)
    sit_floor(m, 0)
    hug_pose(m, 0)
    expr(m, 0, "shock")
    eye_size(m, 0, 1.25)
    # leap to his feet: anticipation squash, launch, airborne, land, recover
    hips(m, 2, loc=(0, 0, -0.32))
    hips(m, 8, loc=(0, 0, 0.22), interp="LINEAR")
    legs(m, 8, l=(-10, 20), r=(10, 30))
    place(m, 8, (-1.1, -0.82, 0.0), 0)
    hips(m, 14, loc=(0, 0, 0.16))
    hips(m, 18, loc=(0, 0, -0.06))
    legs(m, 18, l=(20, 40), r=(20, 40))
    hips(m, 26, loc=(0, 0, 0.0), interp="BACK")
    legs(m, 26, l=(0, 0), r=(0, 0))
    place(m, 18, MPOS, 0)
    place(m, 30, MPOS, MRZ)
    arm(m, "L", 8, fwd=60, out=110, elbow=30)
    arm(m, "R", 8, fwd=60, out=110, elbow=30)
    hug_pose(m, 24)
    head(m, 8, nod=-16)
    head(m, 30, nod=-6, turn=10)
    expr(m, st + 30, "angry")
    talk_bob(m, ctx, "s07_mrx_woii", amp=1.8)
    xbot_akimbo(x, 0)
    xeyes(x, 0, 1.0, 1.0, 1.15)
    ctx.cam(lens=30, fstop=2.4)
    ctx.ck(0, fcam(MPOS, 10, 1.45, 0.7), (-1.1, -0.8, 0.6), focus=(-1.1, -0.95, 0.7))
    ctx.ck(20, fcam(MPOS, 20, 1.45, 0.9), (-1.1, -0.85, 0.85), focus=(-1.1, -1.0, 0.95))
    ctx.ck(60, fcam(MPOS, 24, 1.35, 0.95), (-1.1, -0.85, 0.9), focus=(-1.1, -1.0, 0.95))
    return ctx


@reg
def sh07e(ctx=None):
    def g(ctx, x, m):
        st, ln = ctx.line("s07_xb_dongeng")
        arm(x, "R", st - 2, fwd=-10, out=40, elbow=100)
        arm(x, "R", st + 4, fwd=95, out=-14, elbow=0, interp="BACK")
        xpoint(x, st + 3, "R", True)
        for i, f in enumerate(range(st + 8, st + ln, 8)):    # jabbing
            arm(x, "R", f, fwd=95 + (8 if i % 2 else 0), out=-14, elbow=0)
        pose(x.arm, "body", F(st + 4), rot=(10, 0, 0))
        xeyes(x, st, 1.2, 1.0, 1.25)
    return xbot_talk_shot("sh07e", "s07_xb_dongeng", (1.75, 1.15, 14), lens=30, gesture=g)


@reg
def sh07f(ctx=None):
    ctx, m, x = room_scene("sh07f", ("MRX",))
    bx = mrx_hug_box(ctx, m)
    place(m, 0, MPOS, MRZ)
    hug_pose(m, 0)
    expr(m, 0, "neutral")
    head(m, 2, tilt=-18, nod=-4, interp="BACK")
    gaze(m, 2, 10, 14)
    expr(m, 4, "suspicious")
    blink(m, 16)
    rz = MRZ
    cpos = (MPOS[0] + 0.85 * math.sin(math.radians(rz)), MPOS[1] - 0.85 * math.cos(math.radians(rz)), 0.98)
    ctx.cam(lens=30, fstop=2.2)
    ctx.ck(0, cpos, MHH, focus=MHH)
    ctx.ck(30, (cpos[0], cpos[1], 0.96), MHH, focus=MHH)
    return ctx


def rant(ctx, x, lid, style):
    st, ln = ctx.line(lid)
    if style == "count":       # counting off claims on gloved fingers
        arm(x, "L", st, fwd=80, out=10, elbow=70)
        arm(x, "R", st + 4, fwd=80, out=-30, elbow=90)
        for i, f in enumerate(range(st + 6, st + ln, 10)):
            arm(x, "R", f, fwd=80 + (10 if i % 2 else 0), out=-30, elbow=90)
    elif style == "point":
        arm(x, "R", st, fwd=95, out=-10, elbow=0, interp="BACK")
        xpoint(x, st, "R", True)
        arm(x, "L", st + ln - 14, fwd=30, out=150, elbow=40)
        arm(x, "R", st + ln - 14, fwd=30, out=150, elbow=40)
        xpoint(x, st + ln - 14, "R", False)
    elif style == "checkout":   # mimes tapping a phone "checkout"
        arm(x, "L", st, fwd=75, out=-25, elbow=80)
        arm(x, "R", st, fwd=75, out=-25, elbow=80)
        xpoint(x, st, "R", True)
        for i, f in enumerate(range(st + 4, st + ln, 4)):
            arm(x, "R", f, fwd=75 + (12 if i % 2 else 0), out=-25, elbow=80)
    pose(x.arm, "body", F(st + 2), rot=(8, 0, 0))
    pose(x.arm, "body", F(st + ln), rot=(2, 0, 0))


@reg
def sh07g(ctx=None):
    return xbot_talk_shot("sh07g", "s07_xb_claim80", (1.35, 0.82, -12), lens=32,
                          gesture=lambda c, x, m: rant(c, x, "s07_xb_claim80", "point"))


@reg
def sh07h(ctx=None):
    return xbot_talk_shot("sh07h", "s07_xb_claimown", (1.3, 0.95, 22), lens=32,
                          gesture=lambda c, x, m: rant(c, x, "s07_xb_claimown", "count"))


@reg
def sh07i(ctx=None):
    return xbot_talk_shot("sh07i", "s07_xb_packaging", (1.2, 0.6, -30), lens=30,
                          gesture=lambda c, x, m: rant(c, x, "s07_xb_packaging", "checkout"))


@reg
def sh07j(ctx=None):
    ctx, m, x = room_scene("sh07j", ("MRX",))
    bx = mrx_hug_box(ctx, m)
    rz = MRZ
    place(m, 0, MPOS, rz)
    hug_pose(m, 0)
    expr(m, 0, "embarrassed")
    head(m, 0, nod=14, tilt=6)
    gaze(m, 0, -6, -16)
    # "Tapi..." small, shrinking; "kotak dia cantik..." looks at the box lovingly
    head(m, 10, nod=24, tilt=10)
    chest(m, 10, lean=8)
    hips(m, 12, loc=(0, 0, -0.02))
    for i, f in enumerate(range(14, 34, 5)):          # nervous fidget with the box
        chest(m, f, lean=8, turn=(5 if i % 2 else -5))
    expr(m, 34, "happy")
    gaze(m, 34, 0, -24)
    head(m, 40, nod=28, tilt=-10)
    sparkle(m, 40, True)
    talk_bob(m, ctx, "s07_mrx_tapi", amp=0.8)
    talk_bob(m, ctx, "s07_mrx_cantik", amp=0.9)
    cpos = (MPOS[0] + 0.85 * math.sin(math.radians(rz)), MPOS[1] - 0.85 * math.cos(math.radians(rz)), 0.92)
    ctx.cam(lens=32, fstop=2.2)
    ctx.ck(0, cpos, (MHH[0], MHH[1], 0.92), focus=MHH)
    ctx.ck(70, (cpos[0], cpos[1], 0.9), (MHH[0], MHH[1], 0.9), focus=MHH)
    return ctx


@reg
def sh07k(ctx=None):
    ctx, m, x = room_scene("sh07k", ("XBOT",))
    rz = XRZ
    xbot_akimbo(x, 0)
    xeyes(x, 0, 1.0, 1.0, 1.15)
    # FREEZE. eyes narrow slowly...
    xeyes(x, 15, 1.0, 1.0, 1.15)
    xeyes(x, 45, 0.32, 1.0, 1.1)
    # ...slowly turns to the camera (deadpan)
    place(x, 48, XPOS, rz)
    place(x, 76, XPOS, -4)
    xeyes(x, 80, 0.32, 1.0, 1.1)
    xeyes(x, 90, 0.22, 1.2, 1.1)
    # ASTAGAAA! — explosive: anticipation dip then arms thrown up, eyes huge
    pose(x.arm, "body", F(94), scale=(1.06, 1.06, 0.9))
    arm(x, "L", 94, fwd=-10, out=40, elbow=100)
    arm(x, "R", 94, fwd=-10, out=40, elbow=100)
    arm(x, "L", 100, fwd=20, out=165, elbow=10, interp="BACK")
    arm(x, "R", 100, fwd=20, out=165, elbow=10, interp="BACK")
    pose(x.arm, "body", F(100), scale=(0.93, 0.93, 1.12), interp="BACK")
    pose(x.arm, "body", F(110), scale=(1, 1, 1))
    xeyes(x, 100, 1.35, 0.4, 1.4, interp="BACK")
    ctx.cam(lens=34, fstop=2.4)
    ctx.ck(0, (-0.12, -2.35, 0.86), XH, focus=XH)
    ctx.ck(96, (-0.16, -1.75, 0.84), XH, focus=XH)
    ctx.ck(100, (-0.17, -1.88, 0.82), XH, focus=XH, interp="BACK")
    ctx.ck(120, (-0.17, -1.85, 0.82), XH, focus=XH)
    return ctx


@reg
def sh07l(ctx=None):
    ctx, m, x = room_scene("sh07l", ("XBOT", "MRX"))
    bx = mrx_hug_box(ctx, m)
    place(m, 0, MPOS, MRZ)
    hug_pose(m, 0)
    expr(m, 0, "shock")
    st, ln = ctx.line("s07_xb_kotak")
    rz = XRZ
    # lunges toward MR X with every word, arms wide then double point
    place(x, 0, XPOS, rz)
    place(x, st + 6, (XPOS[0] - 0.14, XPOS[1] + 0.01, 0.08), rz, interp="BACK")
    place(x, st + 12, (XPOS[0] - 0.17, XPOS[1] + 0.01, 0), rz)
    arm(x, "L", 0, fwd=20, out=160, elbow=10)
    arm(x, "R", 0, fwd=20, out=160, elbow=10)
    arm(x, "L", st + 6, fwd=90, out=10, elbow=0, interp="BACK")
    arm(x, "R", st + 6, fwd=90, out=10, elbow=0, interp="BACK")
    xpoint(x, st + 5, "L", True)
    xpoint(x, st + 5, "R", True)
    pose(x.arm, "body", F(st + 6), rot=(14, 0, 0))
    xeyes(x, 0, 1.3, 1.0, 1.35)
    talk_bob(x, ctx, "s07_xb_kotak", amp=2.2, bone="body")
    # MR X recoils from the blast
    head(m, st + 4, nod=-16, interp="BACK")
    chest(m, st + 4, lean=-14)
    eye_size(m, st + 4, 1.3)
    ctx.cam(lens=24, fstop=3.0)
    ctx.ck(0, fcam(XPOS, XRZ, 1.3, 0.38, 30), (-0.45, -0.9, 0.8), focus=XH)
    ctx.ck(65, fcam(XPOS, XRZ, 1.2, 0.40, 30), (-0.5, -0.9, 0.82), focus=XH)
    return ctx


@reg
def sh07m(ctx=None):
    ctx, m, x = room_scene("sh07m")
    bx = mrx_hug_box(ctx, m)
    rz = MRZ
    place(m, 0, MPOS, 0)
    hug_pose(m, 0)
    expr(m, 0, "shock")
    # topples backward onto the bed like a felled tree, bounces, legs kick up
    m.arm.rotation_mode = "XYZ"
    obj_key(m.arm, F(4), loc=MPOS, rot=(0, 0, 0))
    obj_key(m.arm, F(8), loc=MPOS, rot=(6, 0, 0))                  # anticipation
    obj_key(m.arm, F(22), loc=(MPOS[0], MPOS[1] + 0.12, 0.30), rot=(-84, 0, 0), interp="LINEAR")
    obj_key(m.arm, F(26), loc=(MPOS[0], MPOS[1] + 0.12, 0.40), rot=(-80, 0, 0))
    obj_key(m.arm, F(30), loc=(MPOS[0], MPOS[1] + 0.12, 0.33), rot=(-84, 0, 0))
    obj_key(m.arm, F(80), loc=(MPOS[0], MPOS[1] + 0.12, 0.33), rot=(-84, 0, 0))
    legs(m, 20, l=(10, 0), r=(10, 0))
    legs(m, 25, l=(60, 0), r=(50, 10), interp="BACK")
    legs(m, 34, l=(20, 10), r=(15, 10))
    arm(m, "L", 14, fwd=150, out=40, elbow=20)
    arm(m, "R", 14, fwd=150, out=40, elbow=20)
    expr(m, 30, "closed")
    # X-BOT facepalm (slow, weary)
    xbot_akimbo(x, 0)
    xeyes(x, 0, 1.0, 1.0, 1.15)
    arm(x, "R", 30, fwd=-10, out=40, elbow=100)
    arm(x, "R", 42, fwd=110, out=-35, elbow=110, interp="BACK")
    xeyes(x, 40, 0.1, 0.0, 1.0)
    pose(x.arm, "body", F(42), rot=(10, 0, -6))
    pose(x.arm, "body", F(70), rot=(14, 0, -4))
    ctx.cam(lens=24, fstop=3.5)
    ctx.ck(0, (-0.45, -2.9, 1.0), (-0.65, -0.85, 0.6), focus=(-0.8, -0.9, 0.6))
    ctx.ck(80, (-0.5, -2.8, 1.05), (-0.65, -0.8, 0.55), focus=(-0.8, -0.9, 0.6))
    return ctx


# =================================================================== SCENE 08 — LESSON (MR X sits on the bed edge)
BED_SIT = (-1.1, -0.66, 0.05)
BSH = (-1.1, -0.66, 1.02)
XPOS8 = (-0.3, -1.0, 0)
XH8 = (-0.3, -1.0, 0.82)
MRZ8 = 42
XRZ8 = -78


def lesson_scene(sid, chars=("MRX", "XBOT")):
    ctx, m, x = room_scene(sid, chars)
    if m:
        place(m, 0, BED_SIT, MRZ8)
        sit(m, 0, seat_drop=0.0)
        arm(m, "L", 0, fwd=40, out=-10, elbow=40)
        arm(m, "R", 0, fwd=40, out=-10, elbow=40)
        expr(m, 0, "embarrassed")
    if x:
        place(x, 0, XPOS8, XRZ8)
        xbot_akimbo(x, 0)
        xeyes(x, 0, 0.8, 0.2, 1.0)
    return ctx, m, x


def holo(name, img, loc):
    h = plane(name, loc, (0.30, 0.375), m=decal_mat(name, os.path.join(TEX, img), emit_strength=4.0),
              rot=(math.pi / 2, 0, 0))
    h.visible_shadow = False
    return h


@reg
def sh08a(ctx=None):
    ctx, m, x = lesson_scene("sh08a", ("XBOT",))
    rz = XRZ8
    place(x, 0, XPOS8, rz)
    place(x, 14, XPOS8, rz + 45)       # turns to present to us
    xeyes(x, 0, 1.0, 1.0, 1.1)
    xeyes(x, 6, 0.8, 0.1, 1.0)         # calms down
    pose(x.arm, "body", F(0), scale=(1, 1, 1))
    pose(x.arm, "body", F(4), scale=(1.03, 1.03, 0.97))   # exhale
    pose(x.arm, "body", F(12), scale=(1, 1, 1))
    arm(x, "L", 6, fwd=75, out=30, elbow=50)              # palm-up presenting the hologram
    h = holo("holo_ok", "holo_ok.png", (XH8[0] + 0.30, XH8[1] - 0.22, 1.05))
    h.rotation_euler = (math.pi / 2, 0, math.radians(-20))
    obj_key(h, F(4), scale=0.01)
    obj_key(h, F(16), scale=1.0, interp="BACK")
    hl = point("holo_light", (XH8[0] + 0.3, XH8[1] - 0.45, 1.0), energy=0, color=(1.0, 0.8, 0.3), radius=0.2)
    light_key(hl, 4, energy=0)
    light_key(hl, 16, energy=40)
    talk_bob(x, ctx, "s08_xb_dengar", amp=1.0, bone="body")
    ctx.cam(lens=32, fstop=2.6)
    ctx.ck(0, (0.05, -2.3, 0.95), (-0.15, -1.0, 0.95), focus=XH8)
    ctx.ck(85, (0.03, -2.15, 0.95), (-0.15, -1.0, 0.95), focus=XH8)
    return ctx


@reg
def sh08b(ctx=None):
    ctx, m, x = lesson_scene("sh08b", ("XBOT",))
    rz = XRZ8 + 45
    place(x, 0, XPOS8, rz)
    xeyes(x, 0, 0.8, 0.1, 1.0)
    ok = holo("holo_ok", "holo_ok.png", (XH8[0] + 0.30, XH8[1] - 0.22, 1.05))
    bad = holo("holo_bad", "holo_bad.png", (XH8[0] + 0.30, XH8[1] - 0.22, 1.05))
    for h in (ok, bad):
        h.rotation_euler = (math.pi / 2, 0, math.radians(-20))
    show(ok, 0, True)
    show(bad, 0, False)
    show(ok, 50, False)
    show(bad, 50, True)
    obj_key(bad, F(50), scale=0.6)
    obj_key(bad, F(56), scale=1.0, interp="BACK")
    hl = point("holo_light", (XH8[0] + 0.3, XH8[1] - 0.45, 1.0), energy=40, color=(1.0, 0.8, 0.3), radius=0.2)
    light_key(hl, 50, color=(1.0, 0.8, 0.3))
    light_key(hl, 52, color=(1.0, 0.3, 0.2))
    st, ln = ctx.line("s08_xb_salah")
    arm(x, "L", 0, fwd=75, out=30, elbow=50)
    arm(x, "R", st + 30, fwd=-10, out=40, elbow=100)
    arm(x, "R", st + 40, fwd=80, out=50, elbow=10, interp="BACK")   # points at the hologram
    xpoint(x, st + 38, "R", True)
    xeyes(x, st + 40, 1.0, 0.9, 1.1)
    talk_bob(x, ctx, "s08_xb_salah", amp=1.3, bone="body")
    ctx.cam(lens=30, fstop=2.6)
    ctx.ck(0, (0.1, -2.3, 0.98), (-0.12, -1.0, 0.95), focus=(-0.1, -1.05, 0.98))
    ctx.ck(105, (0.08, -2.2, 0.98), (-0.12, -1.0, 0.95), focus=(-0.1, -1.05, 0.98))
    return ctx


@reg
def sh08c(ctx=None):
    ctx, m, x = lesson_scene("sh08c")
    st, ln = ctx.line("s08_xb_fomo")
    arm(x, "R", st, fwd=95, out=-6, elbow=10, interp="BACK")
    xpoint(x, st, "R", True)
    for i, f in enumerate(range(st + 4, st + 40, 6)):     # finger wag: "jangan..."
        arm(x, "R", f, fwd=95, out=-6 + (16 if i % 2 else -10), elbow=10)
    arm(x, "R", st + 50, fwd=60, out=-10, elbow=110)      # taps own temple: "semak dulu"
    xeyes(x, st, 1.0, 0.6, 1.05)
    xeyes(x, st + 50, 0.9, 0.2, 1.0)
    talk_bob(x, ctx, "s08_xb_fomo", amp=1.4, bone="body")
    head(m, st + 10, nod=10, tilt=8)
    gaze(m, st, 6, 0)
    ctx.cam(lens=32, fstop=2.6)
    ctx.ck(0, fcam(XPOS8, XRZ8, 1.55, 1.2, 16), XH8, focus=XH8)
    ctx.ck(100, fcam(XPOS8, XRZ8, 1.45, 1.18, 16), XH8, focus=XH8)
    return ctx


@reg
def sh08d(ctx=None):
    ctx, m, x = lesson_scene("sh08d", ("MRX",))
    st, ln = ctx.line("s08_mrx_faham")
    st2, ln2 = ctx.line("s08_mrx_lepas")
    expr(m, 0, "embarrassed")
    head(m, 0, nod=12, tilt=6)
    gaze(m, 0, 0, -10)
    # sincere: lifts gaze, slow nods, small resolved smile
    gaze(m, st, 6, 4)
    head(m, st + 4, nod=16)
    head(m, st + 12, nod=2)
    head(m, st + 20, nod=12)
    head(m, st2 + 4, nod=0, tilt=-4)
    expr(m, st2, "neutral")
    expr(m, st2 + 20, "happy")
    arm(m, "R", st2 + 10, fwd=40, out=-10, elbow=40)
    arm(m, "R", st2 + 22, fwd=70, out=-30, elbow=120)   # fist to chest: promise
    talk_bob(m, ctx, "s08_mrx_faham", amp=0.7)
    talk_bob(m, ctx, "s08_mrx_lepas", amp=1.0)
    rz = MRZ8
    cpos = (BED_SIT[0] + 0.9 * math.sin(math.radians(rz)), BED_SIT[1] - 0.9 * math.cos(math.radians(rz)), 0.98)
    ctx.cam(lens=32, fstop=2.2)
    ctx.ck(0, cpos, BSH, focus=BSH)
    ctx.ck(80, (cpos[0] * 0.98 + BSH[0] * 0.02, cpos[1] * 0.95 + BSH[1] * 0.05, 0.98), BSH, focus=BSH)
    return ctx


# =================================================================== SCENE 09 — PUNCHLINE
PHONE_AT = (-0.78, -0.42, 0.395)


def punch_scene(sid, chars=("MRX",)):
    ctx, m, x = lesson_scene(sid, chars)
    ph = E.phone("phone", PHONE_AT, rot=(0, 0, math.radians(20)))
    return ctx, m, x, ph


@reg
def sh09a(ctx=None):
    ctx, m, x, ph = punch_scene("sh09a")
    on = bpy.data.objects[ph["on"]]
    off = bpy.data.objects[ph["off"]]
    show(on, 0, False)
    show(off, 0, True)
    show(on, 5, True)
    show(off, 5, False)
    pl = point("phone_glow", (PHONE_AT[0], PHONE_AT[1], 0.5), energy=0, color=(0.7, 0.8, 1.0), radius=0.05)
    light_key(pl, 4, energy=0)
    light_key(pl, 6, energy=25)
    expr(m, 0, "happy")
    head(m, 0, nod=4)
    # TING -> head snaps to phone -> eyes go huge -> hand creeps over
    head(m, 10, nod=18, turn=30, interp="BACK")
    gaze(m, 10, 16, -20)
    expr(m, 14, "shock")
    eye_size(m, 14, 1.0)
    eye_size(m, 18, 1.4, interp="BACK")
    sparkle(m, 18, True)
    arm(m, "L", 24, fwd=40, out=-10, elbow=40)
    arm(m, "L", 70, fwd=45, out=40, elbow=10)
    for i, f in enumerate(range(28, 70, 7)):      # tiny hesitations in the reach
        chest(m, f, lean=6 + (2 if i % 2 else 0), turn=12)
    ctx.cam(lens=30, fstop=1.8)
    ctx.ck(0, (-0.45, -1.1, 0.62), (-0.95, -0.5, 0.7), focus=PHONE_AT)
    ctx.ck(12, (-0.45, -1.1, 0.62), (-0.95, -0.5, 0.72), focus=PHONE_AT)
    ctx.ck(20, (-0.45, -1.08, 0.64), (-1.0, -0.55, 0.85), focus=(-1.05, -0.85, 0.98))   # rack focus to eyes
    ctx.ck(75, (-0.48, -1.02, 0.64), (-1.0, -0.55, 0.85), focus=(-1.05, -0.85, 0.98))
    return ctx


@reg
def sh09b(ctx=None):
    ctx, m, x = lesson_scene("sh09b", ("XBOT",))
    rz = XRZ8
    xeyes(x, 0, 0.6, 1.0, 1.1)
    xeyes(x, 4, 1.3, 1.2, 1.4, interp="BACK")
    pose(x.arm, "body", F(4), rot=(10, 0, 0), scale=(0.95, 0.95, 1.08))
    n = (math.sin(math.radians(rz)), -math.cos(math.radians(rz)))
    eye = (XPOS8[0] + n[0] * 0.16, XPOS8[1] + n[1] * 0.16, 0.80)
    cpos = (XPOS8[0] + n[0] * 0.7, XPOS8[1] + n[1] * 0.7, 0.86)
    ctx.cam(lens=40, fstop=2.0)
    ctx.ck(0, cpos, eye, focus=eye)
    ctx.ck(4, (XPOS8[0] + n[0] * 0.5, XPOS8[1] + n[1] * 0.5, 0.84), eye, focus=eye, interp="BACK")
    ctx.ck(30, (XPOS8[0] + n[0] * 0.46, XPOS8[1] + n[1] * 0.46, 0.84), eye, focus=eye)
    return ctx


@reg
def sh09c(ctx=None):
    ctx, m, x, ph = punch_scene("sh09c")
    on = bpy.data.objects[ph["on"]]
    show(on, 0, True)
    show(bpy.data.objects[ph["off"]], 0, False)
    head(m, 0, nod=18, turn=30)
    arm(m, "L", 0, fwd=45, out=40, elbow=10)
    chest(m, 0, lean=8, turn=12)
    expr(m, 0, "shock")
    eye_size(m, 0, 1.4)
    # caught: freeze with a tiny guilty jolt
    head(m, 4, nod=6, turn=12, interp="BACK")
    eye_size(m, 4, 1.6, interp="BACK")
    hips(m, 4, loc=(0, 0, 0.03))
    rz = MRZ8
    cpos = (BED_SIT[0] + 1.3 * math.sin(math.radians(rz)), BED_SIT[1] - 1.3 * math.cos(math.radians(rz)), 1.0)
    ctx.cam(lens=26, fstop=2.4)
    ctx.ck(0, cpos, BSH, focus=BSH, lens=26)
    ctx.ck(6, cpos, BSH, focus=BSH, lens=62, interp="BACK")
    ctx.ck(15, cpos, BSH, focus=BSH, lens=64)
    return ctx
