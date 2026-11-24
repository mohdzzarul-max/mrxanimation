#!/usr/bin/env python3
"""S01 ROUGH ANIMATION TEST - build the foreground frame sequence.

The six locked key drawings are timed per the X-sheet. Frames between keys are AUTOMATIC
optical-flow in-betweens (OpenCV DIS flow, bidirectional warp + blend). They are a temporary
stand-in for drawn breakdowns and in-betweens, not hand-drawn animation.
Spacing: eased (slow-out/slow-in), on twos, and on ones for the fast reaction (f84-100).

Layers per frame (RGBA, 1920x1080): PROPS (table + flask with violet liquid) + FX (drop, ripple,
bubbles, glow) + character. The background and camera are added later in Blender (comp.json).

  python3 its-x/shots/S01/rough_test/build_rough.py
"""
import os, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS = os.path.join(HERE, '../drawings/keys_approved')
OUT = os.path.join(HERE, 'fg'); os.makedirs(OUT, exist_ok=True)
N = 120
W, H = 1920, 1080

def load(n): return np.asarray(Image.open(os.path.join(KEYS, n + '.png')).convert('RGBA')).astype(np.float32) / 255
K = {k: load(k) for k in ['K01', 'K02', 'K03', 'K04', 'K05', 'K06']}
PROPS = load('PROPS'); GLOW = load('FX_GLOW'); PIP = load('PIPETTE_REST_K01')

# ---------------- timing (frames are 1-based, as on the X-sheet) ----------------
ease = {'io': lambda x: x * x * (3 - 2 * x), 'out': lambda x: 1 - (1 - x) ** 2, 'in': lambda x: x * x}
# (from_key, to_key, start_frame, end_frame, easing); outside segments the key is held
SEG = [('K01', 'K02', 7, 25, 'io'),     # reach: slow-out of the focus hold, slow-in to the grip
       ('K02', 'K03', 29, 37, 'io'),    # lift the dropper (short, so flow ghosting shows for only a few frames)
       ('K03', 'K04', 37, 41, 'out'),   # snap onto the rim for "drop"
       ('K04', 'K05', 55, 69, 'io'),    # after the drop lands: the head turns to the odd pulse
       ('K05', 'K06', 90, 96, 'in')]    # the take: accelerate into "glow" (6 frames on ones, reads as a smear)
ONES = set(range(37, 42)) | set(range(84, 101))

def state(f):
    """(keyA, keyB, t) for frame f, with stepping on twos outside ONES."""
    g = f if f in ONES or f % 2 == 1 else f - 1
    for a, b, s, e, ez in SEG:
        if s <= g < e: return a, b, ease[ez]((g - s) / (e - s))
    held = 'K01'
    for a, b, s, e, ez in SEG:
        if g >= e: held = b
    return held, held, 0.0

# ---------------- optical-flow in-between ----------------
dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
def on_white(img):
    rgb = img[..., :3] * img[..., 3:4] + (1 - img[..., 3:4])
    return cv2.cvtColor((rgb * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
flows = {}
def flow(a, b):
    if (a, b) not in flows:
        ga, gb = [cv2.resize(on_white(K[k]), (W // 2, H // 2)) for k in (a, b)]
        f01 = dis.calc(ga, gb, None); f10 = dis.calc(gb, ga, None)
        up = lambda f: cv2.resize(f, (W, H)) * 2
        flows[(a, b)] = (up(f01), up(f10))
    return flows[(a, b)]
gx, gy = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
def warp(img, fl):
    pm = img.copy(); pm[..., :3] *= pm[..., 3:4]           # premultiplied, so edges don't fringe
    out = cv2.remap(pm, gx + fl[..., 0], gy + fl[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return out
def inbetween(a, b, t):
    if t <= 0.001: return K[a]
    if t >= 0.999: return K[b]
    f01, f10 = flow(a, b)
    ft0 = -(1 - t) * t * f01 + t * t * f10                   # flow from the in-between back to A
    ft1 = (1 - t) ** 2 * f01 - t * (1 - t) * f10              # and forward to B
    w = min(1, max(0, (t - 0.5) * 2.2 + 0.5))                 # sharpened blend: less double-image ghosting
    m = (1 - w) * warp(K[a], ft0) + w * warp(K[b], ft1)
    al = np.clip(m[..., 3:4], 1e-4, 1)
    rgb = np.where(m[..., 3:4] > 1e-3, m[..., :3] / al, 0)
    return np.dstack([np.clip(rgb, 0, 1), np.clip(m[..., 3], 0, 1)])

# ---------------- violet perfume FX ----------------
def intensity(f):
    bump = lambda c, a, w: a * math.exp(-((f - c) / w) ** 2)
    I = bump(49, 0.25, 4) + bump(61, 0.4, 3) + bump(73, 0.55, 3)
    if f >= 80: I += min(1, ((f - 80) / 16) ** 2) * (1 if f <= 96 else max(0.65, 1 - (f - 96) / 30))
    I += bump(109, 0.2, 3)
    return min(I, 1.25)

pa = PROPS[..., 3] > 0.4; pg = PROPS[..., :3].mean(2)
yy = np.arange(H)[:, None]; xx = np.arange(W)[None, :]
LIQ = pa & (yy >= 478) & (yy <= 522) & (xx > 1285) & (xx < 1440) & (pg > 0.45) & (pg < 0.85)  # liquid inside the flask

def fx_layers(f, I, base):
    """Tint the liquid violet (brighter with I) and draw drop / ripple / bubbles. Returns (props_rgba, front_fx_rgba)."""
    props = base.copy()
    liq = np.array([0.55, 0.30, 1.0]) * (0.75 + 0.25 * min(I, 1)) + np.array([0.45, 0.6, 0.0]) * 0.35 * min(I, 1)
    props[LIQ, :3] = props[LIQ, :3] * 0.35 + np.clip(liq, 0, 1) * 0.65
    fxi = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(fxi)
    # ripple where the drop lands (f49-60)
    if 49 <= f <= 60:
        s = (f - 49) / 11; r = 8 + 52 * s
        d.ellipse([1360 - r, 481 - r * 0.18, 1360 + r, 481 + r * 0.18], outline=(235, 210, 255, int(230 * (1 - s))), width=3)
    # bubbles rising in the liquid once it reacts
    rng = np.random.default_rng(7)
    for i in range(22):
        bx, sp, ph, rr = 1300 + rng.random() * 120, 0.5 + rng.random(), rng.random(), 2 + rng.random() * 4
        if i >= int(min(I, 1) * 22) or f < 58: continue
        y = 518 - ((ph + f * sp / 30) % 1) * 38
        d.ellipse([bx - rr, y - rr, bx + rr, y + rr], fill=(250, 235, 255, 210))
    pr = Image.fromarray((props * 255).astype(np.uint8)); pr.alpha_composite(fxi)
    # falling drop: released from the dropper tip at f41, lands on the beat at f49 (gravity)
    front = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(front)
    if 41 <= f < 49:
        s = (f - 41) / 8; y = 372 + (481 - 372) * s * s
        d2.ellipse([1355, y - 9 - 6 * s, 1369, y + 7], fill=(150, 80, 255, 255), outline=(25, 15, 40, 255), width=2)
    return np.asarray(pr).astype(np.float32) / 255, np.asarray(front).astype(np.float32) / 255

def over(dst, src):
    a = src[..., 3:4]
    out = dst.copy(); out[..., :3] = src[..., :3] * a + dst[..., :3] * dst[..., 3:4] * (1 - a)
    out[..., 3:4] = a + dst[..., 3:4] * (1 - a)
    out[..., :3] = np.where(out[..., 3:4] > 1e-4, out[..., :3] / np.clip(out[..., 3:4], 1e-4, 1), 0)
    return out

def glow_layer(I):
    if I <= 0.01: return None
    g = GLOW.copy(); g[..., 3] *= min(1, I)
    big = Image.fromarray((g * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(18 + 30 * min(I, 1)))
    big = np.asarray(big).astype(np.float32) / 255; big[..., 3] = np.clip(big[..., 3] * (1.2 + I), 0, 1)
    return big

log = []
for f in range(1, N + 1):
    a, b, t = state(f); I = intensity(f)
    props, front = fx_layers(f, I, PROPS)
    frame = np.zeros((H, W, 4), np.float32)
    gl = glow_layer(I)
    if gl is not None: frame = over(frame, gl)       # glow halo behind the flask
    frame = over(frame, props)
    if a == 'K01' and b in ('K01', 'K02') and t < 0.5: frame = over(frame, PIP)  # dropper still on the table
    ch = inbetween(a, b, t)
    frame = over(frame, ch)
    frame = over(frame, front)
    if gl is not None and I > 0.5:                     # light spill over the hands and coat
        spill = gl.copy(); spill[..., 3] *= 0.35; frame = over(frame, spill)
    Image.fromarray((np.clip(frame, 0, 1) * 255).astype(np.uint8)).save(os.path.join(OUT, f'{f:04d}.png'))
    log.append(f'{f},{a},{b},{t:.2f},{I:.2f}')
open(os.path.join(HERE, 'frames_log.csv'), 'w').write('frame,from,to,t,intensity\n' + '\n'.join(log) + '\n')
print('wrote', N, 'fg frames to', OUT)
