"""Scenes 01-04: hook, booth, FOMO trap, purchase."""
import math
from mathutils import Vector
from shotkit import *  # noqa
import envs as E

UNC = (0, 0.62, 0)
CUST = (0, -0.45, 0)
UH = (0, 0.62, 1.06)     # uncle head
MH = (0, -0.45, 1.0)     # MR X head at customer spot
SHOTS = {}


def reg(f):
    SHOTS[f.__name__] = f
    return f


def booth_scene(sid, chars=("UNCLE", "MRX")):
    ctx = setup(sid, "booth", chars)
    u = ctx.chars.get("UNCLE")
    m = ctx.chars.get("MRX")
    return ctx, u, m


def uncle_idle(u, ctx, seed=1):
    place(u, 0, UNC, 0)
    expr(u, 0, "neutral")
    smile(u, 0, 0.4)
    blinks(u, 0, ctx.n, seed=seed)
    life(u, 1.0, seed)


def mrx_at_booth(m, ctx, seed=2):
    place(m, 0, CUST, 180)
    expr(m, 0, "neutral")
    blinks(m, 0, ctx.n, seed=seed)
    life(m, 1.0, seed)


def hero_bottle(name="hero_bottle"):
    return E.perfume_bottle(name, (0, 0, 0), s=1.15, liquid=(0.95, 0.5, 0.1), cap="gold")


# =================================================================== SCENE 01
@reg
def sh01(ctx=None):
    ctx = setup("sh01", "bedroom", ["MRX"])
    m = ctx.chars["MRX"]
    H = ctx.H
    place(m, 0, (0.2, -0.6, 0), -15)
    # dramatic hook lighting: hot orange key, blue rim, kill fill
    light_key(H["fill"], 0, energy=5)
    light_key(H["top"], 0, energy=10)
    k = area("hook_key", (0.9, -1.6, 1.4), (0.2, -0.6, 0.95), energy=90, color=(1.0, 0.72, 0.5), size=0.6)
    r = area("hook_rim", (-0.6, 0.4, 1.6), (0.2, -0.6, 1.0), energy=220, color=(0.3, 0.45, 1.0), size=0.5)
    ctx.cam(lens=60, fstop=2.8)
    eye = (0.17, -0.93, 0.97)
    ctx.ck(8, (-0.12, -2.25, 1.0), eye, focus=eye)
    ctx.ck(20, (-0.06, -2.05, 0.99), eye, focus=eye, interp="BACK")
    ctx.ck(92, (-0.04, -1.95, 0.99), eye, focus=eye)
    # performance: smash in, eyes snap wide, recoil, shout
    expr(m, 8, "suspicious")
    head(m, 8, nod=4)
    expr(m, 10, "shock")
    eye_size(m, 8, 1.0)
    eye_size(m, 11, 1.35, interp="BACK")
    eye_size(m, 18, 1.2)
    head(m, 11, nod=-16, tilt=-6)
    chest(m, 11, lean=-10)
    hips(m, 11, loc=(0, 0.05, 0.02))
    arm(m, "L", 8, fwd=4, out=6, elbow=6)
    arm(m, "R", 8, fwd=4, out=6, elbow=6)
    arm(m, "L", 13, fwd=40, out=40, elbow=70, interp="BACK")
    arm(m, "R", 13, fwd=40, out=40, elbow=70, interp="BACK")
    head(m, 30, nod=-8, tilt=6)
    chest(m, 30, lean=-4)
    expr(m, 34, "wide")
    head(m, 60, nod=-6, tilt=-4)
    gaze(m, 60, 0, 0)
    gaze(m, 66, 12, 4)
    gaze(m, 76, -12, 4)
    head(m, 78, nod=-2, tilt=8, turn=-8)
    expr(m, 80, "furious")
    eye_size(m, 80, 1.1)
    head(m, 92, nod=-4, tilt=6, turn=-6)
    talk_bob(m, ctx, "s01_mrx_wehh", amp=1.6)
    return ctx


# =================================================================== SCENE 02
@reg
def sh02a(ctx=None):
    ctx, u, m = booth_scene("sh02a", ("UNCLE",))
    uncle_idle(u, ctx)
    # uncle polishing a bottle on the counter, unaware
    arm(u, "R", 0, fwd=50, out=-10, elbow=40)
    arm(u, "L", 0, fwd=55, out=-15, elbow=45)
    for i, f in enumerate(range(0, 66, 10)):
        arm(u, "R", f, fwd=50, out=-10 + (8 if i % 2 else -4), elbow=40)
    head(u, 0, nod=18)
    ctx.cam(lens=40, fstop=1.8)
    ctx.ck(0, (1.55, 0.55, 1.25), (1.25, 1.1, 1.12), focus=(1.15, 1.08, 1.17))
    ctx.ck(40, (0.95, 0.45, 1.18), (0.6, 0.9, 1.05), focus=(0.8, 1.0, 1.1))
    ctx.ck(65, (0.55, -0.75, 1.15), (0.0, 0.62, 0.92), focus=UH)
    return ctx


@reg
def sh02b(ctx=None):
    ctx, u, m = booth_scene("sh02b", ("UNCLE",))
    uncle_idle(u, ctx)
    ctx.cam(lens=45, fstop=2.2)
    ctx.ck(0, (0.32, -0.85, 1.12), (0, 0.62, 0.95), focus=UH)
    ctx.ck(60, (0.26, -0.70, 1.12), (0, 0.62, 0.97), focus=UH)
    # notices someone off to his right: eyes then head
    head(u, 0, nod=12)
    gaze(u, 0, 0, -10)
    gaze(u, 5, -22, 0, interp="BACK")
    head(u, 9, nod=-2, turn=-28, interp="BACK")
    brows(u, 5, 0, 0)
    brows(u, 9, 1.6, 1.6)
    expr(u, 9, "excited")
    smile(u, 9, 1.0)
    # big friendly wave (anticipation down, then up and oscillate)
    arm(u, "R", 6, fwd=10, out=10, elbow=10)
    arm(u, "R", 12, fwd=30, out=150, elbow=40, interp="BACK")
    for i, f in enumerate(range(16, 54, 6)):
        arm(u, "R", f, fwd=30, out=150 + (12 if i % 2 else -8), elbow=40 + (35 if i % 2 else 0), twist=0)
    arm(u, "L", 12, fwd=25, out=-5, elbow=60)
    chest(u, 12, lean=-4, turn=-10)
    lipsync(u, ctx, "s02_unc_boss", smile_v=0.9)
    return ctx


@reg
def sh02c(ctx=None):
    ctx, u, m = booth_scene("sh02c")
    uncle_idle(u, ctx)
    arm(u, "R", 0, fwd=30, out=150, elbow=60)
    for i, f in enumerate(range(0, 30, 6)):
        arm(u, "R", f, fwd=30, out=150 + (12 if i % 2 else -8), elbow=60 + (30 if i % 2 else 0))
    arm(u, "R", 38, fwd=60, out=-5, elbow=80)   # beckoning toward the counter
    arm(u, "R", 46, fwd=60, out=-5, elbow=110)
    arm(u, "R", 54, fwd=60, out=-5, elbow=80)
    smile(u, 0, 1.0)
    gaze(u, 0, -20, -6)
    gaze(u, 50, 0, -10)
    expr(m, 0, "happy")
    m.walk(F(0), F(46), (-2.0, -1.0, 0), CUST, step_frames=8, bounce=0.025)
    place(m, 50, CUST, 180)
    gaze(m, 0, -10, 6)
    gaze(m, 40, 0, 6)
    blinks(m, 0, 60, seed=4)
    ctx.cam(lens=26, fstop=4)
    ctx.ck(0, (0.35, -2.8, 1.05), (-0.7, -0.4, 0.75), focus=(-1.4, -0.9, 0.8))
    ctx.ck(56, (0.55, -2.6, 1.1), (-0.1, 0.0, 0.8), focus=(0, -0.45, 0.8))
    handheld(ctx, 0.004)
    return ctx


@reg
def sh02d(ctx=None):
    ctx, u, m = booth_scene("sh02d")
    b = hold(u, "R", hero_bottle(), offset=(0.0, -0.07, 0.03))
    uncle_idle(u, ctx)
    mrx_at_booth(m, ctx)
    head(m, 0, nod=-6)
    # lift bottle: anticipation dip, arc up, settle, gentle presenting rotation
    arm(u, "R", 0, fwd=10, out=6, elbow=10, hand=(20, 0, 0))
    arm(u, "R", 8, fwd=5, out=4, elbow=20, hand=(25, 0, 0))
    arm(u, "R", 22, fwd=78, out=-8, elbow=58, hand=(136, 0, 0), interp="BACK")
    arm(u, "R", 50, fwd=82, out=-12, elbow=55, hand=(137, 0, -10))
    arm(u, "R", 78, fwd=80, out=-10, elbow=56, hand=(136, 0, 8))
    arm(u, "L", 24, fwd=60, out=-10, elbow=90)   # hand hovers near bottle, showcasing
    arm(u, "L", 60, fwd=55, out=10, elbow=70)
    brows(u, 10, 1.2, 1.2)
    smile(u, 0, 0.8)
    head(u, 22, nod=-4, tilt=-4)
    gaze(u, 22, 0, -6)
    lipsync(u, ctx, "s02_unc_bukan", smile_v=0.8)
    ctx.cam(lens=50, fstop=2.0)
    ctx.ck(0, (0.62, -1.55, 1.42), (0, 0.62, 0.95), focus=UH)
    ctx.ck(78, (0.55, -1.35, 1.40), (0, 0.62, 0.92), focus=(0, 0.45, 0.9))
    handheld(ctx, 0.003)
    return ctx


@reg
def sh02e(ctx=None):
    ctx, u, m = booth_scene("sh02e", ("UNCLE",))
    b = hold(u, "R", hero_bottle(), offset=(0.0, -0.07, 0.03))
    uncle_idle(u, ctx)
    st, ln = ctx.line("s02_unc_80")
    arm(u, "R", 0, fwd=80, out=-10, elbow=56, hand=(136, 0, 0))
    # beat 1: 80% PATI — thrust the bottle up
    arm(u, "R", st + 2, fwd=72, out=-10, elbow=40, hand=(112, 0, 0))
    arm(u, "R", st + 8, fwd=110, out=-8, elbow=40, hand=(150, 0, 0), interp="BACK")
    head(u, st + 8, nod=-8)
    brows(u, st + 8, 2.2, 2.2)
    # beat 2: OWN CREATION — taps chest proudly with left fist
    arm(u, "L", st + 34, fwd=10, out=6, elbow=10)
    arm(u, "L", st + 40, fwd=50, out=-35, elbow=110)
    arm(u, "L", st + 44, fwd=40, out=-35, elbow=118)
    arm(u, "L", st + 48, fwd=50, out=-35, elbow=110)
    arm(u, "L", st + 52, fwd=40, out=-35, elbow=118)
    arm(u, "R", st + 40, fwd=85, out=-10, elbow=50, hand=(135, 0, 0))
    head(u, st + 40, nod=-12, tilt=6)
    expr(u, st + 40, "smug")
    # beat 3: BUKAN DUPE — wag finger-fist, head shake
    arm(u, "L", st + 70, fwd=70, out=10, elbow=100)
    for i, f in enumerate(range(st + 74, st + 100, 5)):
        arm(u, "L", f, fwd=70, out=10 + (14 if i % 2 else -14), elbow=100)
        head(u, f, nod=-4, turn=(10 if i % 2 else -10))
    expr(u, st + 72, "neutral")
    brows(u, st + 72, 1.5, 1.5, angle=-6)
    head(u, st + 104, nod=-2)
    lipsync(u, ctx, "s02_unc_80", smile_v=0.9, gain=1.1)
    ctx.cam(lens=50, fstop=2.0)
    ctx.ck(0, (0.16, -0.72, 1.02), (0, 0.62, 0.92), focus=(0, 0.45, 0.95))
    ctx.ck(115, (0.08, -0.32, 1.0), (0, 0.62, 0.98), focus=(0, 0.5, 1.0))
    return ctx


@reg
def sh02f(ctx=None):
    ctx, u, m = booth_scene("sh02f", ("MRX",))
    mrx_at_booth(m, ctx)
    st, ln = ctx.line("s02_mrx_fuhh")
    expr(m, 0, "neutral")
    expr(m, st, "excited")
    eye_size(m, 0, 1.0)
    eye_size(m, st + 2, 1.18, interp="BACK")
    sparkle(m, 0, False)
    sparkle(m, st + 6, True)
    head(m, 0, nod=-6)
    head(m, st + 2, nod=-14, interp="BACK")
    chest(m, st + 2, lean=-6)
    # little excited bounces + fists up to chest
    for i, f in enumerate(range(st + 6, st + 80, 8)):
        hips(m, f, loc=(0, 0, 0.03 if i % 2 else -0.005))
    arm(m, "L", st, fwd=4, out=6, elbow=6)
    arm(m, "R", st, fwd=4, out=6, elbow=6)
    arm(m, "L", st + 8, fwd=55, out=-20, elbow=110, interp="BACK")
    arm(m, "R", st + 8, fwd=55, out=-20, elbow=110, interp="BACK")
    head(m, st + 40, nod=-8, tilt=10)
    head(m, st + 70, nod=-10, tilt=-8)
    talk_bob(m, ctx, "s02_mrx_fuhh", amp=1.4)
    ctx.cam(lens=32, fstop=2.0)
    ctx.ck(0, (0.18, 0.35, 1.0), MH, focus=(0, -0.65, 0.98))
    ctx.ck(95, (0.12, 0.15, 1.0), MH, focus=(0, -0.65, 0.98))
    return ctx


@reg
def sh02g(ctx=None):
    ctx, u, m = booth_scene("sh02g", ("UNCLE",))
    b = hold(u, "R", hero_bottle(), offset=(0.0, -0.07, 0.03))
    uncle_idle(u, ctx)
    st, ln = ctx.line("s02_unc_limited")
    arm(u, "R", 0, fwd=80, out=-10, elbow=56, hand=(136, 0, 0))
    arm(u, "L", 0, fwd=10, out=6, elbow=10)
    # "Ha'ah boss!" nod, then sweeping showman arc on "Limited edition!", finger-up "Formula eksklusif!"
    head(u, st, nod=10)
    head(u, st + 6, nod=-6)
    arm(u, "L", st + 14, fwd=40, out=10, elbow=40)
    arm(u, "L", st + 30, fwd=70, out=70, elbow=20, interp="BACK")
    chest(u, st + 30, lean=-4, turn=-8)
    brows(u, st + 30, 2.0, 2.0)
    expr(u, st + 30, "excited")
    arm(u, "L", st + 58, fwd=120, out=10, elbow=60)
    head(u, st + 58, nod=-10, tilt=-6)
    expr(u, st + 60, "smug")
    brows(u, st + 60, 2.4, 0.6)
    arm(u, "R", st + 60, fwd=95, out=-14, elbow=45, hand=(140, 0, 12))
    lipsync(u, ctx, "s02_unc_limited", smile_v=1.0)
    ctx.cam(lens=40, fstop=2.2)
    ctx.ck(0, (-0.3, -0.5, 0.82), (0, 0.62, 1.05), focus=UH)
    ctx.ck(105, (-0.22, -0.3, 0.84), (0, 0.62, 1.07), focus=UH)
    return ctx


@reg
def sh02h(ctx=None):
    ctx, u, m = booth_scene("sh02h", ("MRX",))
    mrx_at_booth(m, ctx)
    expr(m, 0, "excited")
    sparkle(m, 0, True)
    eye_size(m, 0, 1.15)
    eye_size(m, 6, 1.55, interp="BACK")
    eye_size(m, 40, 1.65)
    eye_size(m, 44, 1.5)
    expr(m, 6, "shock")
    arm(m, "L", 0, fwd=55, out=-20, elbow=110)
    arm(m, "R", 0, fwd=55, out=-20, elbow=110)
    arm(m, "L", 6, fwd=70, out=-30, elbow=130, interp="BACK")
    arm(m, "R", 6, fwd=70, out=-30, elbow=130, interp="BACK")
    for i, f in enumerate(range(6, 60, 2)):   # FOMO jitter vibration
        hips(m, f, loc=((0.006 if i % 2 else -0.006), 0, 0.01 + (0.008 if i % 3 == 0 else 0)))
    head(m, 6, nod=-16)
    ctx.cam(lens=40, fstop=2.0)
    ctx.ck(0, (0.0, 0.25, 1.0), MH, focus=(0, -0.7, 0.98))
    ctx.ck(40, (0.0, 0.05, 1.0), MH, focus=(0, -0.7, 0.98), interp="CONSTANT")
    ctx.ck(41, (0.0, 0.18, 0.98), MH, focus=(0, -0.7, 0.98))
    ctx.ck(60, (0.0, 0.14, 0.98), MH, focus=(0, -0.7, 0.98))
    return ctx


# =================================================================== SCENE 03
def mrx_box_hold(m, ctx, bx):
    arm(m, "R", 0, fwd=72, out=-28, elbow=40, hand=(112, 0, 0))
    arm(m, "L", 0, fwd=72, out=-28, elbow=40, hand=(112, 0, 0))


@reg
def sh03a(ctx=None):
    ctx, u, m = booth_scene("sh03a", ("MRX",))
    bx = hold(m, "R", E.perfume_box("buy_box", s=1.1), offset=(0.08, -0.07, -0.05))
    mrx_at_booth(m, ctx)
    mrx_box_hold(m, ctx, bx)
    ctx.sc.frame_set(F(0))
    p = bx.matrix_world.translation + Vector((0, 0, 0.11))
    ctx.cam(lens=70, fstop=1.6)
    ctx.ck(0, p + Vector((0.32, 0.30, 0.04)), p, focus=p + Vector((0, 0.04, 0)))
    ctx.ck(66, p + Vector((-0.12, 0.42, 0.0)), p + Vector((0, 0, 0.01)), focus=p + Vector((0, 0.04, 0)))
    for f in (0, 33, 66):
        arm(m, "R", f, fwd=72 + (3 if f == 33 else 0), out=-28, elbow=40, hand=(112, 0, (6 if f == 33 else -4)))
    return ctx


@reg
def sh03b(ctx=None):
    ctx, u, m = booth_scene("sh03b", ("MRX",))
    bx = hold(m, "R", E.perfume_box("buy_box", s=1.1), offset=(0.08, -0.07, -0.05))
    mrx_at_booth(m, ctx)
    mrx_box_hold(m, ctx, bx)
    st, ln = ctx.line("s03_mrx_betul")
    gaze(m, 0, 0, -18)
    head(m, 0, nod=14)
    expr(m, 0, "neutral")
    expr(m, st, "suspicious", interp="BACK")
    gaze(m, st + 2, 0, 8)
    head(m, st + 4, nod=-6, tilt=14)
    head(m, st + 40, nod=-4, tilt=16, turn=6)
    expr(m, st + 44, "squint")
    gaze(m, st + 44, 8, 6)
    head(m, st + 70, nod=-2, tilt=10, turn=10)
    hips(m, st, loc=(0, 0, 0))
    hips(m, st + 30, loc=(0, 0.03, 0))   # leans in slightly
    talk_bob(m, ctx, "s03_mrx_betul", amp=1.0)
    ctx.cam(lens=32, fstop=2.0)
    ctx.ck(0, (0.3, 0.25, 0.95), (0, -0.45, 0.92), focus=(0, -0.65, 0.95))
    ctx.ck(92, (0.22, 0.12, 0.97), (0, -0.45, 0.95), focus=(0, -0.65, 0.97))
    return ctx


@reg
def sh03c(ctx=None):
    ctx, u, m = booth_scene("sh03c", ("UNCLE",))
    uncle_idle(u, ctx)
    st, ln = ctx.line("s03_unc_alaa")
    # "Alaaa boss!" dismissive wave
    arm(u, "L", st, fwd=10, out=6, elbow=10)
    arm(u, "L", st + 8, fwd=60, out=30, elbow=60, hand=(0, 0, 0), interp="BACK")
    arm(u, "L", st + 14, fwd=60, out=50, elbow=40)
    arm(u, "L", st + 22, fwd=20, out=8, elbow=20)
    head(u, st + 4, nod=6, turn=12, tilt=-8)
    expr(u, st + 4, "happy")
    smile(u, st, 1.0)
    # "Uncle sendiri cipta formula ni" — chest taps
    tap0 = st + 56
    arm(u, "R", tap0 - 10, fwd=10, out=6, elbow=10)
    for i, f in enumerate(range(tap0, tap0 + 24, 6)):
        arm(u, "R", f, fwd=48, out=-40, elbow=(112 if i % 2 else 120))
    head(u, tap0, nod=-14, tilt=4)
    brows(u, tap0, 2.4, 2.4)
    expr(u, tap0, "smug")
    # "Rahsia tujuh keturunan!" lean in, conspiratorial, finger up, glasses glint
    arm(u, "R", tap0 + 34, fwd=100, out=-6, elbow=80)
    chest(u, tap0 + 34, lean=10)
    head(u, tap0 + 34, nod=4, turn=-6)
    brows(u, tap0 + 38, 0.4, 2.2, angle=-4)
    expr(u, tap0 + 40, "squint")
    gaze(u, tap0 + 40, -6, 0)
    head(u, 100, nod=-6, tilt=-8, turn=4)
    chest(u, 150, lean=4)
    lipsync(u, ctx, "s03_unc_alaa", smile_v=0.9)
    gl = area("glint_light", (0.6, -0.9, 1.4), UH, energy=0, color=(1.0, 0.75, 0.3), size=0.15)
    light_key(gl, 96, energy=0)
    light_key(gl, 100, energy=300)
    light_key(gl, 108, energy=0)
    ctx.cam(lens=50, fstop=2.0)
    ctx.ck(0, (0.22, -0.55, 1.06), UH, focus=(0, 0.42, 1.05))
    ctx.ck(96, (0.12, -0.25, 1.05), UH, focus=(0, 0.42, 1.05))
    ctx.ck(108, (0.08, -0.22, 1.04), UH, focus=(0, 0.42, 1.05), interp="BACK")
    ctx.ck(160, (0.07, -0.18, 1.04), UH, focus=(0, 0.42, 1.05))
    return ctx


@reg
def sh03d(ctx=None):
    ctx, u, m = booth_scene("sh03d", ("MRX",))
    bx = hold(m, "R", E.perfume_box("buy_box", s=1.1), offset=(0.08, -0.07, -0.05))
    mrx_at_booth(m, ctx)
    mrx_box_hold(m, ctx, bx)
    expr(m, 0, "neutral")
    expr(m, 4, "excited", interp="BACK")
    eye_size(m, 0, 1.0)
    eye_size(m, 6, 1.35, interp="BACK")
    sparkle(m, 5, True)
    head(m, 0, nod=0)
    head(m, 6, nod=-18, tilt=-6, interp="BACK")
    gaze(m, 6, 0, 18)
    ctx.cam(lens=35, fstop=1.8)
    ctx.ck(0, (0.06, 0.45, 1.0), MH, focus=(0, -0.7, 0.98))
    ctx.ck(30, (0.0, 0.16, 1.0), MH, focus=(0, -0.7, 0.98))
    return ctx


@reg
def sh03e(ctx=None):
    ctx = setup("sh03e", "runway", ["MRX"])
    m = ctx.chars["MRX"]
    H = ctx.H
    expr(m, 0, "smug")
    m.walk(F(0), F(64), (0, 4.6, 0), (0, 1.3, 0), step_frames=10, bounce=0.03)
    place(m, 66, (0, 1.3, 0), 0)
    # swagger: head bob + chest sway while walking
    for i, f in enumerate(range(0, 64, 10)):
        chest(m, f, lean=-4, tilt=(5 if i % 2 else -5))
        head(m, f, nod=-6, tilt=(-4 if i % 2 else 4))
    # hero pose: anticipation crouch then fist to the sky, wind-blown
    hips(m, 68, loc=(0, 0, -0.04))
    arm(m, "R", 66, fwd=10, out=10, elbow=20)
    arm(m, "R", 76, fwd=165, out=10, elbow=10, interp="BACK")
    arm(m, "L", 76, fwd=10, out=30, elbow=80)
    hips(m, 76, loc=(0, 0, 0.02), interp="BACK")
    chest(m, 76, lean=-12, tilt=-6)
    head(m, 76, nod=-14, tilt=8)
    expr(m, 76, "happy")
    sparkle(m, 76, True)
    blink(m, 40, "smug")
    for i, fl in enumerate(H["flashes"]):
        for k in range(4):
            f = (i * 17 + k * 29) % 108
            show(fl, f, True)
            show(fl, f + 2, False)
    ctx.cam(lens=35, fstop=2.2)
    ctx.ck(0, (0.25, -0.2, 0.42), (0, 3.6, 0.85), focus=(0, 4.3, 0.8))
    ctx.ck(64, (0.15, -0.6, 0.38), (0, 1.3, 0.85), focus=(0, 1.25, 0.8))
    ctx.ck(80, (0.05, -0.15, 0.32), (0, 1.3, 1.0), focus=(0, 1.2, 0.9), interp="BACK")
    ctx.ck(110, (0.02, -0.08, 0.30), (0, 1.3, 1.02), focus=(0, 1.2, 0.9))
    return ctx


@reg
def sh03f(ctx=None):
    ctx, u, m = booth_scene("sh03f", ("MRX",))
    mrx_at_booth(m, ctx)
    st, ln = ctx.line("s03_mrx_on")
    expr(m, 0, "excited")
    eye_size(m, 0, 1.2)
    # snap back to reality: blink-shake, then decisive fist pump
    head(m, 0, nod=-10, tilt=10)
    head(m, 3, nod=-2, tilt=-10)
    head(m, 6, nod=-6, tilt=0)
    arm(m, "R", 10, fwd=20, out=10, elbow=40)
    arm(m, "R", 18, fwd=120, out=-10, elbow=120, interp="BACK")
    arm(m, "R", 23, fwd=80, out=-10, elbow=130)       # pump down
    arm(m, "R", 27, fwd=115, out=-10, elbow=120)
    hips(m, 18, loc=(0, 0, -0.03))
    hips(m, 23, loc=(0, 0, 0.04), interp="BACK")
    hips(m, 30, loc=(0, 0, 0))
    expr(m, 22, "happy")
    head(m, 30, nod=-10, tilt=6)
    talk_bob(m, ctx, "s03_mrx_on", amp=1.6)
    ctx.cam(lens=32, fstop=2.0)
    ctx.ck(0, (0.18, 0.18, 1.0), MH, focus=(0, -0.65, 0.98))
    ctx.ck(55, (0.12, 0.05, 1.0), MH, focus=(0, -0.65, 0.98))
    return ctx


@reg
def sh03g(ctx=None):
    ctx, u, m = booth_scene("sh03g")
    note = hold(m, "R", E.note_single("mrx_note", (0, 0, 0), s=1.0, rot=(0, math.radians(90), 0)),
                offset=(0, -0.06, 0.02))
    show(note, 0, False)
    show(note, 30, True)
    uncle_idle(u, ctx)
    mrx_at_booth(m, ctx)
    st, ln = ctx.line("s03_unc_bagus")
    arm(u, "R", st, fwd=70, out=-10, elbow=60)
    arm(u, "R", st + 6, fwd=95, out=-10, elbow=40, interp="BACK")   # thumbs-up-ish fist
    head(u, st + 6, nod=-8, tilt=6)
    smile(u, st, 1.0)
    brows(u, st + 4, 2.0, 2.0)
    # MR X digs in pocket, pulls out the cash
    arm(m, "R", 10, fwd=-30, out=20, elbow=60)
    arm(m, "R", 18, fwd=-35, out=25, elbow=70)
    head(m, 12, nod=14, turn=-20)
    arm(m, "R", 30, fwd=-20, out=20, elbow=60)
    arm(m, "R", 40, fwd=70, out=-10, elbow=30, interp="BACK")
    head(m, 40, nod=-4)
    expr(m, 40, "happy")
    lipsync(u, ctx, "s03_unc_bagus", smile_v=1.0)
    ctx.cam(lens=32, fstop=3.0)
    ctx.ck(0, (1.65, 0.05, 1.0), (0, 0.1, 0.88), focus=(0, 0.1, 0.9))
    ctx.ck(45, (1.55, -0.05, 1.0), (0, 0.08, 0.88), focus=(0, 0.1, 0.9))
    return ctx


# =================================================================== SCENE 04
@reg
def sh04a(ctx=None):
    ctx, u, m = booth_scene("sh04a")
    note_m = hold(m, "R", E.note_single("mrx_note", (0, 0, 0), s=1.0, rot=(0, math.radians(90), 0)),
                  offset=(0, -0.06, 0.02))
    note_u = hold(u, "R", E.note_single("unc_note", (0, 0, 0), s=1.0, rot=(0, math.radians(90), 0)),
                  offset=(0, -0.07, 0.02))
    uncle_idle(u, ctx)
    mrx_at_booth(m, ctx)
    show(note_m, 0, True)
    show(note_u, 0, False)
    show(note_m, 46, False)
    show(note_u, 46, True)
    # slow-motion: long eased extension
    arm(m, "R", 0, fwd=50, out=-5, elbow=40)
    arm(m, "R", 44, fwd=82, out=-16, elbow=8)
    arm(m, "R", 60, fwd=60, out=-5, elbow=30)
    arm(u, "R", 10, fwd=20, out=0, elbow=30)
    arm(u, "R", 46, fwd=80, out=-22, elbow=12)
    arm(u, "R", 72, fwd=45, out=-10, elbow=95)   # tucks cash to chest
    head(u, 0, nod=4)
    gaze(u, 0, 0, -10)
    gaze(u, 30, -4, -22)
    gaze(u, 50, -6, -30)
    gaze(u, 70, 0, -14)
    head(u, 50, nod=14, turn=-4)
    expr(u, 30, "excited")
    smile(u, 0, 0.6)
    smile(u, 56, 1.0)
    brows(u, 50, 2.2, 2.2)
    gl = area("glint_light", (0.5, -0.8, 1.3), UH, energy=0, color=(1.0, 0.75, 0.3), size=0.15)
    light_key(gl, 48, energy=0)
    light_key(gl, 52, energy=260)
    light_key(gl, 62, energy=0)
    ctx.cam(lens=45, fstop=2.0)
    ctx.ck(0, (0.62, -0.42, 0.98), (0.0, 0.15, 0.78), focus=(0.05, 0.05, 0.72))
    ctx.ck(75, (0.55, -0.3, 0.96), (0.0, 0.2, 0.82), focus=(0.0, 0.15, 0.78))
    return ctx


@reg
def sh04b(ctx=None):
    ctx, u, m = booth_scene("sh04b")
    bx = hold(u, "R", E.perfume_box("sell_box", s=1.1), offset=(0.08, -0.08, -0.04))
    uncle_idle(u, ctx)
    mrx_at_booth(m, ctx)
    st, ln = ctx.line("s04_unc_terbaik")
    arm(u, "R", 0, fwd=40, out=-10, elbow=60, hand=(100, 0, 0))
    arm(u, "R", st + 20, fwd=85, out=-10, elbow=25, hand=(110, 0, 0), interp="BACK")
    arm(u, "L", st + 10, fwd=60, out=10, elbow=90)
    arm(u, "L", st + 30, fwd=100, out=0, elbow=70)
    head(u, st + 4, nod=-8, tilt=6)
    brows(u, st + 4, 2.0, 2.0)
    expr(u, st + 4, "happy")
    head(u, st + 40, nod=8, tilt=-4)   # little bow
    arm(m, "L", 40, fwd=60, out=-20, elbow=40)
    arm(m, "R", 40, fwd=60, out=-20, elbow=40)
    expr(m, 30, "excited")
    lipsync(u, ctx, "s04_unc_terbaik", smile_v=1.0)
    ctx.cam(lens=45, fstop=2.2)
    ctx.ck(0, (-0.42, -1.4, 1.25), (0, 0.55, 0.92), focus=(0, 0.5, 0.95))
    ctx.ck(72, (-0.36, -1.22, 1.22), (0, 0.5, 0.9), focus=(0, 0.45, 0.95))
    return ctx


@reg
def sh04c(ctx=None):
    ctx, u, m = booth_scene("sh04c")
    bx = hold(m, "R", E.perfume_box("hug_box", s=1.1), offset=(0.12, -0.09, 0.08))
    uncle_idle(u, ctx)
    place(m, 0, CUST, 180)
    expr(m, 0, "happy")
    sparkle(m, 0, True)
    # hug the box like treasure
    arm(m, "R", 0, fwd=70, out=-40, elbow=70, hand=(130, 0, 0))
    arm(m, "L", 0, fwd=70, out=-40, elbow=80)
    head(m, 0, nod=12, tilt=10)
    for i, f in enumerate(range(0, 16, 4)):
        chest(m, f, turn=(8 if i % 2 else -8))
    m.walk(F(18), F(90), CUST, (-2.4, -1.4, 0), step_frames=8, arms=False, bounce=0.04)
    for f in range(18, 90, 8):
        arm(m, "R", f, fwd=70, out=-40, elbow=70, hand=(130, 0, 0))
        arm(m, "L", f, fwd=70, out=-40, elbow=80)
    st, ln = ctx.line("s04_unc_terima")
    arm(u, "R", st - 6, fwd=20, out=10, elbow=20)
    arm(u, "R", st, fwd=30, out=150, elbow=40, interp="BACK")
    for i, f in enumerate(range(st + 4, st + 56, 6)):
        arm(u, "R", f, fwd=30, out=150 + (12 if i % 2 else -8), elbow=40 + (35 if i % 2 else 0))
    smile(u, 0, 1.0)
    gaze(u, 20, -20, -6)
    head(u, 30, turn=-20)
    lipsync(u, ctx, "s04_unc_terima", smile_v=1.0)
    ctx.cam(lens=26, fstop=4.0)
    ctx.ck(0, (0.7, -2.8, 1.1), (-0.3, 0.0, 0.75), focus=(0, -0.45, 0.8))
    ctx.ck(100, (0.6, -2.7, 1.1), (-0.6, -0.2, 0.75), focus=(-1.2, -0.9, 0.8))
    return ctx


@reg
def sh04d(ctx=None):
    ctx, u, m = booth_scene("sh04d", ("UNCLE",))
    uncle_idle(u, ctx)
    H = ctx.H
    arm(u, "R", 0, fwd=30, out=150, elbow=40)
    arm(u, "R", 6, fwd=30, out=140, elbow=70)
    arm(u, "R", 26, fwd=6, out=8, elbow=10)
    head(u, 0, turn=-20)
    smile(u, 0, 1.0)
    brows(u, 0, 1.5, 1.5)
    gaze(u, 0, -20, -4)
    # smile fades... hold... the turn
    smile(u, 30, 0.2)
    brows(u, 34, 0.0, 0.0)
    head(u, 40, turn=-8)
    gaze(u, 46, -12, 0)
    expr(u, 50, "neutral")
    expr(u, 58, "smug")
    head(u, 66, turn=4, nod=-4, tilt=-6)
    gaze(u, 66, 8, 2)                      # side-eye to the audience
    brows(u, 62, 1.8, -0.8, angle=6)
    smile(u, 64, 0.2)
    smile(u, 80, 1.0)                      # slow sly grin
    arm(u, "L", 70, fwd=10, out=6, elbow=10)
    arm(u, "L", 88, fwd=55, out=-30, elbow=120)   # rubs chin
    light_key(H["key"], 0, energy=260, color=(1.0, 0.78, 0.55))
    light_key(H["key"], 40, energy=260, color=(1.0, 0.78, 0.55))
    light_key(H["key"], 80, energy=120, color=(1.0, 0.6, 0.35))
    light_key(H["rim"], 40, energy=180)
    light_key(H["rim"], 80, energy=420, color=(0.35, 0.5, 1.0))
    light_key(H["top"], 40, energy=220)
    light_key(H["top"], 80, energy=60)
    ctx.cam(lens=50, fstop=2.0)
    ctx.ck(0, (0.1, -0.95, 1.06), UH, focus=(0, 0.42, 1.05))
    ctx.ck(95, (0.04, -0.30, 1.04), (0, 0.62, 1.06), focus=(0, 0.42, 1.05))
    return ctx
