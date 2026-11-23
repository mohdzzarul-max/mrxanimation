"""ZSCENTS clearance ad - polish render.
Pass 1: read source, flip (fix mirrored footage), grade each source frame (cached).
Pass 2: build edit timeline (crops, B-roll, push-ins, sweeps, type) -> raw frames to ffmpeg.
Audio is built separately (audio.py) and muxed at the end; the original voice track is untouched in timing.
"""
import sys, json, math, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = '/root/.claude/uploads/6372891a-b8b6-550d-800d-91a8e1dbdf79/f44b129d-lv_0_20261123210257.mp4'
W, H, FPS = 1080, 1920, 30
NOUT = 649  # 21.633 s
PREVIEW = [int(x) for x in sys.argv[1].split(',')] if len(sys.argv) > 1 else None

# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out_expo(t): t = clamp(t); return 1 - 2 ** (-10 * t) if t < 1 else 1.0
def ease_in_out_cubic(t):
    t = clamp(t); return 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2
def ease_out_cubic(t): t = clamp(t); return 1 - (1 - t) ** 3
def lerp(a, b, t): return a + (b - a) * t

# ---------------------------------------------------------------- bottle track
track = json.load(open(os.path.join(HERE, 'track.json')))
def bottle_track():
    """Reliable label-artwork anchors -> smoothed bottle centre/size per source frame."""
    anchors = {}
    for r in track:
        if r[1] is None: continue
        i, x, y, w, h = r[0], r[1], r[2], r[3], r[4]
        if ((w >= 130 and h >= 120) or (w >= 140 and h >= 85)) and (i <= 60 or 396 <= i <= 570):
            anchors[i] = (x + w / 2, y + h / 2, max(w, h))
    out = {}
    for lo, hi in ((0, 60), (396, 570)):
        ks = sorted(k for k in anchors if lo <= k <= hi)
        if not ks: continue
        idx = np.arange(ks[0], ks[-1] + 1)
        arr = np.array([anchors[k] for k in ks])
        cols = [np.interp(idx, ks, arr[:, c]) for c in range(3)]
        # gaussian smooth (sigma 2.5 frames) for stable framing
        g = np.exp(-0.5 * (np.arange(-8, 9) / 2.5) ** 2); g /= g.sum()
        cols = [np.convolve(np.pad(c, 8, mode='edge'), g, 'valid') for c in cols]
        for j, i in enumerate(idx):
            out[int(i)] = (cols[0][j], cols[1][j], cols[2][j])
    return out
BT = bottle_track()

def bottle_box(i):
    """bottle (cap + glass) box in source coords: x0,y0,x1,y1"""
    if i not in BT: return None
    ax, ay, s = BT[i]
    return (ax - 0.80 * s, ay - 1.75 * s, ax + 0.80 * s, ay + 0.95 * s)

# ---------------------------------------------------------------- grading
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
SEG = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path=os.path.join(HERE, 'models/seg.tflite')),
    output_confidence_masks=True))

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
# soft key-light pool behind the subject (upper middle) + falloff -> depth
pool = np.exp(-(((xx - 560) / 620) ** 2 + ((yy - 640) / 820) ** 2))
BG_MUL = (0.40 + 0.34 * pool) * (1.0 - 0.10 * (yy / H))
VIG = 1.0 - 0.30 * np.clip((((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.45) / (H * 0.62)) ** 2), 0, 1.6) ** 1.4
_prev_mask = None

def person_mask(rgb):
    r = SEG.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)))
    bg = r.confidence_masks[0].numpy_view()
    m = cv2.resize(1.0 - bg, (W, H), interpolation=cv2.INTER_LINEAR)
    return cv2.GaussianBlur(m, (0, 0), 6)

def grade(bgr_u8, i, sequential=True):
    global _prev_mask
    rgb = cv2.cvtColor(bgr_u8, cv2.COLOR_BGR2RGB)
    img = bgr_u8.astype(np.float32) / 255.0
    P = person_mask(rgb)
    if sequential and _prev_mask is not None:
        P = 0.65 * P + 0.35 * _prev_mask          # temporal smoothing, kills edge flicker
    _prev_mask = P
    bb = bottle_box(i)
    B = np.zeros((H, W), np.float32)
    if bb:
        x0, y0, x1, y1 = [int(v) for v in bb]
        cv2.rectangle(B, (x0, y0), (x1, y1), 1.0, -1)
        B = cv2.GaussianBlur(B, (0, 0), 14)
    S = np.clip(np.maximum(P, B), 0, 1)
    S3 = S[..., None]
    lum = img @ np.array([0.114, 0.587, 0.299], np.float32)

    # --- background: lower exposure, warm-neutral editorial tone, light pool for separation
    bg = img * BG_MUL[..., None] * np.array([0.95, 0.985, 1.03], np.float32)

    # --- subject: gentle filmic S-curve, blacks kept dense but with texture
    sub = img.copy()
    sc = sub * sub * (3 - 2 * sub)
    sub = sub * 0.78 + sc * 0.22
    # local contrast (large-radius unsharp on luminance) -> knit/mask detail without crushing
    blur = cv2.GaussianBlur(lum, (0, 0), 18)
    sub = sub + (0.22 * (lum - blur))[..., None]
    # eye-hole illumination: skin visible through the mask
    hsv = cv2.cvtColor(bgr_u8, cv2.COLOR_BGR2HSV)
    skin = ((hsv[..., 0] < 25) & (hsv[..., 1] > 35) & (hsv[..., 1] < 175) & (hsv[..., 2] > 55)).astype(np.float32)
    skin[1000:] = 0
    skin *= P
    if bb: skin *= (1 - B)
    skin = cv2.GaussianBlur(skin, (0, 0), 16)
    skin = np.clip(skin * 2.2, 0, 1)
    sub = sub * (1 + 0.20 * skin[..., None]) + 0.012 * skin[..., None]
    # directional rim / key highlight from upper-left (+ weaker upper-right kicker)
    Pm = cv2.GaussianBlur(P, (0, 0), 3)
    sh_l = np.roll(np.roll(Pm, 18, 0), 18, 1)     # value of pixel up-left
    sh_r = np.roll(np.roll(Pm, 14, 0), -14, 1)
    rim = Pm * (1 - sh_l) + 0.45 * Pm * (1 - sh_r)
    rim = cv2.GaussianBlur(rim, (0, 0), 7)
    rim *= (1 - B)
    dark = np.clip(1 - lum * 1.6, 0, 1)
    sub = sub + (rim * dark * 0.30)[..., None] * np.array([0.80, 0.90, 1.0], np.float32)
    # soft top-down key falloff on subject (shoulders/head brighter than belly)
    sub = sub * (1.02 - 0.12 * (yy / H))[..., None]

    # --- bottle: local exposure + clarity + label sharpening (real pixels only)
    if bb:
        Bc = B[..., None]
        bot = img * 1.10
        bl = cv2.GaussianBlur(bot, (0, 0), 1.6)
        bot = bot + 0.85 * (bot - bl)
        bl2 = cv2.GaussianBlur(bot, (0, 0), 10)
        bot = bot + 0.25 * (bot - bl2)
        sub = sub * (1 - Bc) + bot * Bc

    out = bg * (1 - S3) + sub * S3
    out = out * VIG[..., None]
    out = np.clip(out, 0, 1)
    # highlight roll-off
    out = 1 - (1 - out) ** 1.04
    return (out * 255 + 0.5).astype(np.uint8)

# ---------------------------------------------------------------- source cache
needed = set(range(0, 60)) | set(range(76, 400)) | set(range(396, 570))
def load_and_grade(indices):
    cap = cv2.VideoCapture(SRC)
    cache = {}
    i = 0
    maxi = max(indices)
    while i <= maxi:
        ok, f = cap.read()
        if not ok: break
        if i in indices:
            f = cv2.flip(f, 1)                     # fix mirrored footage
            cache[i] = grade(f, i, sequential=(i - 1 in cache))
        i += 1
    return cache

# ---------------------------------------------------------------- shots / timeline
# each shot: (out_start, out_end_inclusive, src_fn(local_t 0..1, f) -> float src index, cam_fn(f)-> (zoom, cx, cy), tag)
def bcenter(i):
    i = int(round(i))
    if i in BT:
        ax, ay, s = BT[i]
        return ax, ay - 0.40 * s
    return 540, 1100

SHOTS = []
def shot(a, b, src, cam, tag): SHOTS.append((a, b, src, cam, tag))

# S1 HOOK 0-52: src 10->52 slightly slowed; fast expo push-in toward bottle+mask
def cam_hook(f):
    t = f / 52
    z = lerp(1.24, 1.60, ease_out_expo(f / 14)) + 0.05 * t
    return z, lerp(430, 360, ease_out_expo(f / 14)), lerp(1000, 1010, ease_out_expo(f / 14))
shot(0, 52, lambda f: 10 + (f) * (42 / 52), cam_hook, 'hook')

# S2 wall replacement 53-80: bottle close-up from src 504-531
def cam_tight(z0, z1, n, oy=0):
    def c(f, i):
        z = lerp(z0, z1, ease_in_out_cubic(f / n))
        cx, cy = bcenter(i)
        return z, cx, cy + oy
    return c
shot(53, 80, lambda f: 542 + f * (18 / 27), cam_tight(1.85, 1.98, 27, oy=240), 'broll')
# S3 presenter 81-201 with punch-ins
def cam_pres(keys):
    # keys: list of (frame, zoom, cx, cy, hard) ; hard punch = 3-frame snap with ease
    def c(f, i):
        k = [x for x in keys if x[0] <= f][-1]
        nxt = [x for x in keys if x[0] > f]
        prevk = [x for x in keys if x[0] < k[0]]
        z, cx, cy = k[1], k[2], k[3]
        if prevk and f - k[0] < 4:  # 4-frame eased snap from previous framing (no hard pop)
            p = prevk[-1]; t = ease_out_cubic((f - k[0] + 1) / 4)
            z, cx, cy = lerp(p[1], z, t), lerp(p[2], cx, t), lerp(p[3], cy, t)
        # slow drift toward next key
        drift = 0.0006 * (f - k[0])
        return z + drift, cx, cy
    return c
FACE = (540, 820)
shot(81, 201, lambda f: 81 + f, cam_pres([(0, 1.10, 540, 860, 0), (45, 1.26, 540, 760, 1), (81, 1.08, 540, 900, 1)]), 'pres')
# S4 B-roll on "ZSCENTS": src 26-38 slowed (label detail)
shot(202, 222, lambda f: 456 + f, cam_tight(1.90, 2.02, 20, oy=240), 'broll')
# S5 presenter 223-280, punch on "clearance stock" (7.9s -> f237)
shot(223, 280, lambda f: 223 + f, cam_pres([(0, 1.12, 540, 860, 0), (14, 1.28, 540, 760, 1), (31, 1.10, 540, 880, 1)]), 'pres')
# S6 B-roll on "stock ZSCENTS": src 542-559
shot(281, 298, lambda f: 26 + f * (12 / 17), cam_tight(2.0, 2.1, 17, oy=230), 'broll')
# S7 presenter 299-395, punch on "Bawah RM55" (11.9s -> f357)
shot(299, 395, lambda f: 299 + f, cam_pres([(0, 1.08, 540, 900, 0), (58, 1.24, 540, 780, 1)]), 'pres')
# S8 PRODUCT SPOTLIGHT 396-541: in place, bottle-follow framing
def cam_spot(f, i):
    t = f / 145
    z = lerp(1.70, 1.92, ease_in_out_cubic(t))
    if f >= 110:  # hero slow-mo tail: tighter on the sharpest frames
        z = lerp(1.95, 2.08, ease_in_out_cubic((f - 110) / 35))
        cx, cy = bcenter(i)
        return z, cx, cy + 230
    cx, cy = bcenter(i)
    # keep some of the mask in frame, bias framing so bottle sits above captions
    return z, lerp(cx, 540, 0.30), cy + 300
shot(396, 541, lambda f: 396 + f if f < 110 else 462 + (f - 110) * (16 / 35), cam_spot, 'spot')
# S9 presenter "Ok," 542-569
shot(542, 569, lambda f: 542 + f, cam_pres([(0, 1.12, 540, 860, 0)]), 'pres')
# S10 END HERO 570-648: sharpest bottle frame (src 474) with slow push
def cam_end(f, i):
    z = lerp(1.55, 1.70, ease_in_out_cubic(f / 78))
    cx, cy = bcenter(474)
    return z, cx, cy + 50
shot(570, 648, lambda f: 474, cam_end, 'end')

def shot_for(fo):
    for s in SHOTS:
        if s[0] <= fo <= s[1]: return s
    raise KeyError(fo)

def get_src(cache, x):
    a = int(math.floor(x)); t = x - a
    fa = cache[a]
    if t < 0.08 or (a + 1) not in cache: return fa
    return cv2.addWeighted(fa, 1 - t, cache[a + 1], t, 0)

def crop(img, z, cx, cy):
    cw, ch = W / z, H / z
    cx = clamp(cx, cw / 2, W - cw / 2); cy = clamp(cy, ch / 2, H - ch / 2)
    x0, y0 = cx - cw / 2, cy - ch / 2
    M = np.float32([[z, 0, -x0 * z], [0, z, -y0 * z]])
    out = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    return out, (x0, y0, z)

def to_out(pt, xf):
    x0, y0, z = xf
    return ((pt[0] - x0) * z, (pt[1] - y0) * z)

# ---------------------------------------------------------------- effects
def light_sweep(img, box, t, strength=0.38):
    """diagonal soft highlight band travelling across the bottle glass (screen blend, bottle area only)"""
    if box is None or not (0 <= t <= 1): return img
    x0, y0, x1, y1 = box
    m = np.zeros((H, W), np.float32)
    cv2.rectangle(m, (int(x0), int(y0)), (int(x1), int(y1)), 1.0, -1)
    m = cv2.GaussianBlur(m, (0, 0), 10)
    bw = (x1 - x0)
    pos = lerp(x0 - bw * 0.7, x1 + bw * 0.7, ease_in_out_cubic(t))
    d = (xx - pos) + (yy - (y0 + y1) / 2) * 0.42
    band = np.exp(-(d / (bw * 0.10)) ** 2) + 0.35 * np.exp(-((d + bw * 0.22) / (bw * 0.05)) ** 2)
    a = (band * m * strength * math.sin(math.pi * t) ** 0.6)[..., None]
    f = img.astype(np.float32) / 255
    f = 1 - (1 - f) * (1 - a * np.array([0.93, 0.97, 1.0], np.float32))  # screen, warm-white
    return (f * 255).astype(np.uint8)

def motion_blur(img, amount, vertical=False):
    k = int(amount)
    if k < 3: return img
    ker = np.zeros((k, k), np.float32)
    if vertical: ker[:, k // 2] = 1
    else: ker[k // 2, :] = 1
    return cv2.filter2D(img, -1, ker / k)

GRAIN = np.random.default_rng(7).normal(0, 1, (8, H // 2, W // 2)).astype(np.float32)
def grain(img, fo):
    g = cv2.resize(GRAIN[fo % 8], (W, H), interpolation=cv2.INTER_LINEAR)
    f = img.astype(np.float32) + g[..., None] * 3.2
    return np.clip(f, 0, 255).astype(np.uint8)

# ---------------------------------------------------------------- typography
F_CAP = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
def serif(size, wght=700, path='fonts/PlayfairDisplay.ttf'):
    f = ImageFont.truetype(os.path.join(HERE, path), size)
    f.set_variation_by_axes([wght]); return f
CAPF = ImageFont.truetype(F_CAP, 66)
IVORY = (246, 238, 224); GOLD = (236, 182, 92)

# caption chunks anchored to the speech energy envelope (original Malay audio, unchanged)
# (start, end, text, gold-words, style)   style: cap | accent
CHUNKS = [
    (0.10, 1.10, '55ml', ['55ml'], 'hook'),
    (3.02, 3.62, 'Eh,', [], 'cap'),
    (3.62, 4.45, 'JANGAN SCROLL', ['SCROLL'], 'accent'),
    (4.45, 5.20, 'jangan scroll lagi', ['lagi'], 'cap'),
    (5.38, 6.45, 'Tunggu dulu.', ['Tunggu'], 'cap'),
    (6.72, 7.32, 'ZSCENTS', ['ZSCENTS'], 'cap'),
    (7.32, 7.92, 'sekarang ni tengah buat', [], 'cap'),
    (7.92, 8.48, 'CLEARANCE STOCK', ['STOCK'], 'accent'),
    (8.48, 9.36, 'Nak clearkan semua', [], 'cap'),
    (9.36, 10.00, 'stock ZSCENTS.', ['ZSCENTS.'], 'cap'),
    (10.34, 11.14, 'Dengan harga', [], 'cap'),
    (11.14, 11.90, 'sangat mampu milik.', ['mampu', 'milik.'], 'cap'),
    (11.90, 12.84, 'BAWAH RM55', ['RM55'], 'accent'),
    (12.84, 13.18, 'untuk', [], 'cap'),
    (13.18, 14.60, 'untuk 55ml.', ['55ml.'], 'cap'),
    (15.12, 15.60, 'So korang', [], 'cap'),
    (15.60, 16.18, 'tunggu apa lagi?', [], 'cap'),
    (16.18, 16.95, 'Dapatkan segera', ['Dapatkan', 'segera'], 'cap'),
    (16.95, 17.55, 'sementara stock', [], 'cap'),
    (17.55, 18.30, 'masih ada.', ['masih', 'ada.'], 'cap'),
    (18.62, 19.08, 'Ok,', [], 'cap'),
    (19.08, 20.20, 'now boleh scroll guys.', [], 'cap'),
]

def text_layer(draw_fn):
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw_fn(layer)
    return layer

def draw_shadowed(base, xy, text, font, fill, alpha=1.0, shadow=0.75, spacing=0, anchor='mm'):
    """text with soft drop shadow; letter spacing support"""
    if alpha <= 0.01: return
    tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    if spacing:
        widths = [font.getlength(ch) for ch in text]
        total = sum(widths) + spacing * (len(text) - 1)
        x = xy[0] - total / 2
        for ch, w in zip(text, widths):
            d.text((x, xy[1]), ch, font=font, fill=fill + (255,), anchor='lm')
            x += w + spacing
    else:
        d.text(xy, text, font=font, fill=fill + (255,), anchor=anchor)
    a = tmp.getchannel('A')
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * shadow)))
    sh = sh.transform((W, H), Image.AFFINE, (1, 0, 0, 0, 1, -4))
    tmp.putalpha(a.point(lambda v: int(v * alpha)))
    sh.putalpha(sh.getchannel('A').point(lambda v: int(v * alpha)))
    base.alpha_composite(sh); base.alpha_composite(tmp)

def draw_rich_line(base, cx, cy, words, golds, font, alpha, dy):
    space = font.getlength(' ')
    ws = [font.getlength(w) for w in words]
    total = sum(ws) + space * (len(words) - 1)
    x = cx - total / 2
    for w, wl in zip(words, ws):
        col = GOLD if w in golds else IVORY
        draw_shadowed(base, (x + wl / 2, cy + dy), w, font, col, alpha)
        x += wl + space

def caption_y(fo):
    tag = shot_for(fo)[4]
    return {'spot': 1470, 'end': 1660}.get(tag, 1400)

def draw_text(fo):
    t = fo / FPS
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for (a, b, text, golds, style) in CHUNKS:
        if not (a - 0.01 <= t < b + 0.02): continue
        tin = (t - a) / 0.18; tout = (t - (b - 0.07)) / 0.08
        alpha = ease_out_cubic(tin) * (1 - clamp(tout))
        dy = 22 * (1 - ease_out_cubic(tin))
        cx = 520  # nudged left of TikTok right-rail icons
        if style == 'cap':
            words = text.split()
            lines = [words] if len(text) <= 22 else [words[:len(words) // 2 + len(words) % 2], words[len(words) // 2 + len(words) % 2:]]
            y = caption_y(fo) - (len(lines) - 1) * 38
            for li, ln in enumerate(lines):
                draw_rich_line(layer, cx, y + li * 78, ln, golds, CAPF, alpha, dy)
        elif style == 'accent':
            # stacked serif headline, per-letter stagger reveal + gold hairline
            f = serif(128, 800)
            parts = text.split()
            y0 = caption_y(fo) - 50
            for li, w in enumerate(parts):
                col = GOLD if w in golds else IVORY
                n = len(w)
                widths = [f.getlength(ch) for ch in w]
                sp = 6
                tot = sum(widths) + sp * (n - 1)
                x = cx - tot / 2
                for ci, (ch, cw) in enumerate(zip(w, widths)):
                    lt = (t - a - 0.025 * (ci + li * n * 0.5)) / 0.22
                    la = ease_out_expo(lt) * (1 - clamp(tout))
                    ldy = 40 * (1 - ease_out_expo(lt))
                    draw_shadowed(layer, (x + cw / 2, y0 + li * 140 + ldy), ch, f, col, la, shadow=0.85)
                    x += cw + sp
            # hairline
            lt = ease_out_expo((t - a - 0.08) / 0.35) * (1 - clamp(tout))
            if lt > 0.01:
                d = ImageDraw.Draw(layer)
                hw = 180 * lt
                d.line([(cx - hw, y0 + 230), (cx + hw, y0 + 230)], fill=GOLD + (int(220 * lt),), width=3)
        elif style == 'hook':
            # big '55ml' on the clean right side, away from the bottle
            f = serif(230, 700)
            s = 1.0 + 0.10 * (1 - ease_out_expo(tin))
            lt = ease_out_expo(tin) * (1 - clamp(tout))
            fs = serif(int(230 * s), 700)
            draw_shadowed(layer, (800, 1330 + dy), '55', fs, IVORY, lt, shadow=0.9)
            draw_shadowed(layer, (800, 1490 + dy), 'ml', serif(int(120 * s), 500), GOLD, lt, shadow=0.9)
            ht = ease_out_expo((t - a - 0.1) / 0.4) * (1 - clamp(tout))
            if ht > 0.01:
                d = ImageDraw.Draw(layer)
                d.line([(800 - 120 * ht, 1565), (800 + 120 * ht, 1565)], fill=GOLD + (int(230 * ht),), width=3)
    # end card wordmark (brand name is spoken in the ad)
    if fo >= 572:
        lt = ease_out_expo((fo - 576) / 22)
        draw_shadowed(layer, (540, 300), 'ZSCENTS', serif(96, 600, 'fonts/Cinzel.ttf'), IVORY, lt, shadow=0.8, spacing=int(lerp(40, 22, lt)))
        ht = ease_out_expo((fo - 586) / 20)
        if ht > 0.01:
            d = ImageDraw.Draw(layer)
            d.line([(540 - 150 * ht, 372), (540 + 150 * ht, 372)], fill=GOLD + (int(220 * ht),), width=3)
    return layer

# ---------------------------------------------------------------- frame assembly
SWEEPS = [(5, 20), (397, 414), (582, 606)]   # (start,end) out frames
def render_frame(cache, fo):
    a, b, srcf, cam, tag = shot_for(fo)
    f = fo - a
    si = srcf(f)
    img = get_src(cache, si)
    if tag == 'hook':
        z, cx, cy = cam(f)
    else:
        z, cx, cy = cam(f, int(round(si)))
    # transition energy: first frames of a shot inherit a short zoom-settle + directional motion blur
    if tag == 'spot' and f >= 110: f = f - 110
    if tag in ('broll', 'spot', 'end') and f < 5:
        z *= 1 + 0.07 * (1 - ease_out_cubic((f + 1) / 5))
    if tag == 'pres' and f < 4 and a > 0:
        z *= 1 - 0.05 * (1 - ease_out_cubic((f + 1) / 4))
    out, xf = crop(img, z, cx, cy)
    if f < 3 and a > 0:
        out = motion_blur(out, [26, 14, 6][f], vertical=(tag == 'pres'))
    if fo > 0 and fo == b:  # last frame of a shot: blur into the cut
        nxt = shot_for(fo + 1)[4] if fo + 1 < NOUT else None
        if nxt: out = motion_blur(out, 12, vertical=(nxt == 'pres'))
    # sweeps across the real bottle
    bb = bottle_box(int(round(si)))
    for s0, s1 in SWEEPS:
        if s0 <= fo <= s1 and bb:
            p0 = to_out(bb[:2], xf); p1 = to_out(bb[2:], xf)
            out = light_sweep(out, (p0[0], p0[1], p1[0], p1[1]), (fo - s0) / (s1 - s0))
    # hook flash: 2-frame exposure lift on the impact, decays
    if fo < 6:
        out = cv2.convertScaleAbs(out, alpha=1 + 0.18 * (1 - fo / 6), beta=10 * (1 - fo / 6))
    # end card: deepen surround so bottle glows
    if tag == 'end':
        k = ease_out_cubic(f / 18)
        out = (out.astype(np.float32) * (1 - 0.38 * k * (1 - END_SPOT))).astype(np.uint8)
    out = grain(out, fo)
    pil = Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).convert('RGBA')
    pil.alpha_composite(draw_text(fo))
    return cv2.cvtColor(np.array(pil.convert('RGB')), cv2.COLOR_RGB2BGR)

END_SPOT = np.exp(-(((xx - 540) / 480) ** 2 + ((yy - 930) / 560) ** 2))[..., None]

if __name__ == '__main__':
    import subprocess
    frames = PREVIEW if PREVIEW else list(range(NOUT))
    need = set()
    for fo in frames:
        a, b, srcf, cam, tag = shot_for(fo)
        x = srcf(fo - a); need |= {int(math.floor(x)), int(math.floor(x)) + 1}
    # grade contiguous runs for temporal mask smoothing
    full = set()
    for n in need: full |= set(range(max(0, n - 2), n + 1))
    if not PREVIEW: full = needed | need
    cache = load_and_grade(full)
    print('graded', len(cache), flush=True)
    if PREVIEW:
        for fo in frames:
            cv2.imwrite(os.path.join(HERE, f'prev4/p{fo:03d}.jpg'), render_frame(cache, fo), [cv2.IMWRITE_JPEG_QUALITY, 92])
        sys.exit(0)
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', '30',
                          '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p',
                          '-profile:v', 'high', '-movflags', '+faststart', os.path.join(HERE, 'video_only.mp4')], stdin=subprocess.PIPE)
    for fo in range(NOUT):
        p.stdin.write(render_frame(cache, fo).tobytes())
        if fo % 50 == 0: print('frame', fo, flush=True)
    p.stdin.close(); p.wait()
    print('done')
