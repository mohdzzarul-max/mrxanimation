"""Compositing / motion graphics / grading / subtitles  (the "After Effects" stage).

Reads 3D renders (renders/<shot>/NNNN.png) + timeline.py, writes 1080x1920 frames to renders/_comp/NNNNN.jpg
and subtitles/MRX_EP01_ms.srt.   Usage: python3 composite.py [shot ...]  (default: all, parallel)
"""
import json, math, os, random, sys
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageChops, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import timeline as TL  # noqa
from script_data import LINE  # noqa

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
REN = os.path.join(ROOT, "renders")
OUT = os.path.join(REN, "_comp")
FONTS = os.path.join(ROOT, "source", "fonts")
W, H = 1080, 1920
DUR = json.load(open(os.path.join(ROOT, "voices", "durations.json")))
YELLOW = (255, 206, 40)
RED = (255, 52, 52)
WHITE = (255, 255, 255)
GOLD = (226, 182, 90)


def font(w, s):
    return ImageFont.truetype(os.path.join(FONTS, f"Montserrat-{w}.ttf"), int(s))


def ease_out_back(t, s=1.70158):
    t = min(max(t, 0), 1) - 1
    return t * t * ((s + 1) * t + s) + 1


def ease_out(t):
    t = min(max(t, 0), 1)
    return 1 - (1 - t) ** 3


# ------------------------------------------------------------------ source frames
_cache = {}


def src_frame(sid, lf, spec):
    r0, r1 = spec["render"]
    if r1 <= r0:
        return Image.new("RGB", (W, H), (0, 0, 0))
    lf = min(max(lf, r0), r1 - 1)
    p = os.path.join(REN, sid, f"{lf:04d}.png")
    if not os.path.exists(p):   # not rendered yet: nearest available, else slate
        av = sorted(os.listdir(os.path.join(REN, sid))) if os.path.isdir(os.path.join(REN, sid)) else []
        if not av:
            im = Image.new("RGB", (W, H), (20, 20, 24))
            ImageDraw.Draw(im).text((80, 900), f"[{sid} rendering]", font=font("Bold", 60), fill=(120, 120, 120))
            return im
        p = os.path.join(REN, sid, min(av, key=lambda n: abs(int(n[:4]) - lf)))
    im = Image.open(p).convert("RGB")
    if im.size != (W, H):
        im = im.resize((W, H), Image.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(radius=2.2, percent=70, threshold=2))
    return im


# ------------------------------------------------------------------ grade
_grain = np.random.default_rng(3).normal(0, 1, (8, H // 2, W // 2)).astype(np.float32)
_vig = None


def grade(im, f, warm=0.0, vig=0.55, bloom=0.32):
    global _vig
    a = np.asarray(im).astype(np.float32) / 255
    # bloom: blur of bright areas
    small = im.resize((W // 4, H // 4), Image.BILINEAR)
    sa = np.asarray(small).astype(np.float32) / 255
    br = np.clip(sa - 0.62, 0, 1) * 2.2
    bl = Image.fromarray((np.clip(br, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(14))
    bl = np.asarray(bl.resize((W, H), Image.BILINEAR)).astype(np.float32) / 255
    a = a + bl * bloom * np.array([1.0, 0.85, 0.65])
    # split tone: warm highlights / cool shadows (reference look)
    lum = (a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11)[..., None]
    a = a + (1 - lum) ** 2 * np.array([-0.012, 0.0, 0.03]) + lum ** 2 * np.array([0.035, 0.012, -0.03]) * (1 + warm)
    # gentle S-curve
    a = np.clip(a, 0, 1)
    a = a + 0.10 * (a - a ** 2) * (2 * a - 1) * -1
    # vignette
    if _vig is None:
        yy, xx = np.mgrid[0:H, 0:W]
        d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 * 0.8 + ((yy - H / 2) / (H / 2)) ** 2)
        _vig = np.clip(1 - (d - 0.55) * 0.55, 0.45, 1)[..., None].astype(np.float32)
    a = a * (1 - vig + vig * _vig)
    g = np.asarray(Image.fromarray(((_grain[f % 8] * 0.5 + 0.5) * 255).clip(0, 255).astype(np.uint8)).resize((W, H)))
    a = a + (g[..., None].astype(np.float32) / 255 - 0.5) * 0.035
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


# ------------------------------------------------------------------ text
def draw_text(im, text, cx, cy, size, fill, weight="Black", stroke=None, scale=1.0, rot=0.0, alpha=1.0,
              shadow=True, maxw=None):
    if scale <= 0.01 or alpha <= 0.01:
        return im
    s = size * scale
    f = font(weight, s)
    dummy = ImageDraw.Draw(im)
    tw = dummy.textlength(text, font=f)
    if maxw and tw > maxw:
        s *= maxw / tw
        f = font(weight, s)
        tw = dummy.textlength(text, font=f)
    sw = stroke if stroke is not None else max(3, int(s * 0.08))
    pad = int(sw * 3 + s * 0.4)
    layer = Image.new("RGBA", (int(tw) + pad * 2, int(s * 1.3) + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if shadow:
        d.text((pad + s * 0.05, pad + s * 0.07), text, font=f, fill=(0, 0, 0, int(160 * alpha)), stroke_width=sw,
               stroke_fill=(0, 0, 0, int(160 * alpha)))
    d.text((pad, pad), text, font=f, fill=(*fill, int(255 * alpha)), stroke_width=sw,
           stroke_fill=(0, 0, 0, int(255 * alpha)))
    if rot:
        layer = layer.rotate(rot, resample=Image.BICUBIC, expand=True)
    im.paste(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)), layer)
    return im


def text_pop(im, lf, f0, t, y, col, size, life=40):
    k = lf - f0
    if k < 0 or k > life:
        return im
    sc = ease_out_back(k / 7) if k < 7 else 1.0 + 0.02 * math.sin(k * 0.4)
    al = 1.0 if k < life - 6 else (life - k) / 6
    return draw_text(im, t, W / 2, H * y, size, {"yellow": YELLOW, "white": WHITE, "red": RED}[col], scale=sc,
                     rot=-3 + 6 * ((hash(t) % 7) / 7), alpha=al, maxw=W * 0.9)


def text_stamp(im, lf, f0, t, y, col, size, life=40):
    k = lf - f0
    if k < 0 or k > life:
        return im
    sc = 2.4 - 1.4 * ease_out(k / 4) if k < 4 else 1.0
    al = min(1, k / 2 + 0.3) if k < life - 6 else (life - k) / 6
    return draw_text(im, t, W / 2, H * y, size, {"yellow": YELLOW, "white": WHITE, "red": RED}[col], scale=sc,
                     rot=-4, alpha=al, maxw=W * 0.92)


# ------------------------------------------------------------------ fx building blocks
def star(d, cx, cy, r, col, a=255):
    pts = []
    for i in range(8):
        ang = i * math.pi / 4
        rr = r if i % 2 == 0 else r * 0.22
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=(*col, a))


def overlay(im, layer):
    im = im.convert("RGBA")
    im.alpha_composite(layer)
    return im.convert("RGB")


def sparkles(im, lf, f0, dur, seed=1):
    k = lf - f0
    if k < 0 or k > dur:
        return im
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    rnd = random.Random(seed)
    for i in range(22):
        x, y = rnd.uniform(80, W - 80), rnd.uniform(400, 1300)
        ph = rnd.uniform(0, 6.28)
        sz = (0.5 + 0.5 * math.sin(k * 0.35 + ph)) * rnd.uniform(14, 34)
        star(d, x, y - k * 1.5, sz, (255, 230, 150), 230)
    L = L.filter(ImageFilter.GaussianBlur(0.8))
    return overlay(im, L)


def lightsweep(im, lf, f0, dur):
    k = lf - f0
    if k < 0 or k > dur:
        return im
    t = k / dur
    L = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(L)
    x = -600 + t * (W + 1200)
    d.polygon([(x, 0), (x + 220, 0), (x - 380, H), (x - 600, H)], fill=110)
    L = L.filter(ImageFilter.GaussianBlur(60))
    warm = Image.new("RGB", (W, H), (255, 225, 170))
    return Image.composite(ImageChops.screen(im, warm), im, L)


def glint(im, lf, f0, x, y, dur=12):
    k = lf - f0
    if k < 0 or k > dur:
        return im
    a = math.sin(math.pi * k / dur)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    cx, cy = W * x, H * y
    r = 180 * a
    d.polygon([(cx - r, cy), (cx, cy - 10), (cx + r, cy), (cx, cy + 10)], fill=(255, 240, 200, int(230 * a)))
    d.polygon([(cx, cy - r * 0.7), (cx - 8, cy), (cx, cy + r * 0.7), (cx + 8, cy)], fill=(255, 240, 200, int(230 * a)))
    d.ellipse([cx - 26 * a, cy - 26 * a, cx + 26 * a, cy + 26 * a], fill=(255, 255, 255, int(255 * a)))
    return overlay(im, L.filter(ImageFilter.GaussianBlur(2)))


def flash(im, lf, f0, dur, col=(255, 255, 255)):
    k = lf - f0
    if k < 0 or k > dur:
        return im
    return Image.blend(im, Image.new("RGB", (W, H), col), 0.85 * (1 - k / dur))


def speedlines(im, lf, col=(255, 255, 255), n=60, alpha=120, seed=0):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    rnd = random.Random(seed + lf // 2)
    cx, cy = W / 2, H * 0.45
    for i in range(n):
        ang = rnd.uniform(0, 2 * math.pi)
        r0 = rnd.uniform(520, 760)
        r1 = r0 + rnd.uniform(300, 900)
        wdt = rnd.uniform(2, 9)
        p0 = (cx + r0 * math.cos(ang), cy + r0 * math.sin(ang))
        p1 = (cx + r1 * math.cos(ang), cy + r1 * math.sin(ang))
        d.line([p0, p1], fill=(*col, alpha), width=int(wdt))
    return overlay(im, L)


def anger(im, lf, f0, dur):
    k = lf - f0
    if k < 0 or k > dur:
        return im
    ramp = min(1, k / 4)
    red = Image.new("RGB", (W, H), (200, 10, 10))
    im = Image.blend(im, ImageChops.multiply(im, Image.new("RGB", (W, H), (255, 120, 110))), 0.5 * ramp)
    im = Image.blend(im, red, 0.10 * ramp * (0.7 + 0.3 * math.sin(k * 0.8)))
    im = speedlines(im, lf, (255, 230, 220), 70, 110)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    # steam puffs rising from the head
    for i in range(6):
        ph = (k * 2.5 + i * 22) % 120
        x = W / 2 + (-260 if i % 2 else 260) + math.sin(ph * 0.1 + i) * 30
        y = 520 - ph * 3
        r = 30 + ph * 0.8
        d.ellipse([x - r, y - r, x + r, y + r], fill=(240, 240, 240, int(max(0, 170 - ph * 1.4))))
    # anime anger vein (cross mark)
    if (k // 6) % 2 == 0:
        vx, vy, s = W * 0.73, H * 0.21, 70
        for ang in (45, 135, 225, 315):
            a = math.radians(ang)
            p = (vx + s * 0.35 * math.cos(a), vy + s * 0.35 * math.sin(a))
            d.arc([p[0] - s * 0.45, p[1] - s * 0.45, p[0] + s * 0.45, p[1] + s * 0.45], ang + 90, ang + 270,
                  fill=(255, 40, 40, 255), width=16)
    return overlay(im, L.filter(ImageFilter.GaussianBlur(1.5)))


def shockwave(im, lf, f0, x, y, col):
    k = lf - f0
    if k < 0 or k > 18:
        return im
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    c = {"yellow": (255, 200, 40)}.get(col, (255, 255, 255))
    for j, lag in enumerate((0, 3)):
        kk = k - lag
        if kk < 0:
            continue
        r = 60 + ease_out(kk / 14) * 1400
        a = int(255 * max(0, 1 - kk / 16))
        cx, cy = W * x, H * y
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(*c, a), width=int(40 - kk * 2) if kk < 18 else 2)
    L = L.filter(ImageFilter.GaussianBlur(3))
    im = overlay(im, L)
    if k < 6:
        im = Image.blend(im, Image.new("RGB", (W, H), c), 0.45 * (1 - k / 6))
    return im


def impact_frame(im):
    g = ImageOps.grayscale(im)
    g = ImageOps.autocontrast(g, cutoff=8)
    g = g.point(lambda v: 255 if v > 110 else 0)
    return ImageOps.invert(g).convert("RGB")


def fomo_meter(im, lf, f0, dur):
    k = lf - f0
    if k < 0 or k > dur:
        return im
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    x0, y0, w, h = 120, 300, W - 240, 70
    sc = ease_out_back(k / 8)
    if sc < 0.05:
        return im
    val = min(99, int(ease_out(k / 30) * 99))
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], 35, fill=(0, 0, 0, 180), outline=(*WHITE, 255), width=6)
    fillw = (w - 16) * val / 100
    col = (255, int(200 - 170 * val / 100), 40)
    d.rounded_rectangle([x0 + 8, y0 + 8, x0 + 8 + fillw, y0 + h - 8], 28, fill=(*col, 255))
    im = overlay(im, L)
    draw_text(im, f"FOMO LEVEL: {val}%", W / 2, y0 - 70, 74, YELLOW, scale=sc)
    if val >= 99 and (k // 3) % 2 == 0:
        draw_text(im, "FOMO ACTIVATED", W / 2, y0 + h + 80, 66, RED, scale=1.0, rot=-3)
    return im


def label_call(im, lf, f0, t, dur):
    k = lf - f0
    if k < 0 or k > dur:
        return im
    a = min(1, k / 5) if k < dur - 5 else (dur - k) / 5
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    y = 1060
    d.rounded_rectangle([90, y - 60, W - 90, y + 60], 20, fill=(10, 10, 12, int(200 * a)),
                        outline=(*YELLOW, int(255 * a)), width=5)
    d.line([(W * 0.55, y + 60), (W * 0.62, y + 180)], fill=(*YELLOW, int(255 * a)), width=6)
    im = overlay(im, L)
    return draw_text(im, t, W / 2, y, 44, YELLOW, weight="ExtraBold", alpha=a, maxw=W - 220, shadow=False)


def inset(im, lf, f0, src, src_start, dur, t):
    k = lf - f0
    if k < 0 or k > dur:
        return im
    sp = TL_SPEC[src]
    frm = src_frame(src, src_start + k, sp)
    frm = ImageOps.grayscale(frm).convert("RGB")
    frm = ImageChops.multiply(frm, Image.new("RGB", (W, H), (255, 225, 175)))
    sc = ease_out_back(k / 8) * 0.5
    if sc < 0.05:
        return im
    w, h = int(W * sc), int(H * sc * 0.62)
    frm = frm.crop((0, int(H * 0.19), W, int(H * 0.81))).resize((w, h))
    bord = Image.new("RGB", (w + 24, h + 24), WHITE)
    bord.paste(frm, (12, 12))
    bord = bord.rotate(4, expand=True, fillcolor=(0, 0, 0))
    mask = bord.convert("L").point(lambda v: 255 if v > 0 else 0)
    x, y = int(W * 0.5 - bord.width / 2), 170
    im.paste(bord, (x, y), mask)
    draw_text(im, "FLASHBACK", x + 150, y + 30, 40, WHITE, rot=4, scale=min(1, k / 6))
    draw_text(im, t, W / 2, y + bord.height + 10, 70, YELLOW, rot=-3, scale=ease_out_back(max(0, k - 6) / 7))
    return im


def notif(im, lf, f0, dur):
    k = lf - f0
    if k < 0 or k > dur:
        return im
    yy = -220 + 380 * ease_out_back(k / 9)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    d.rounded_rectangle([60, yy, W - 60, yy + 240], 44, fill=(248, 248, 250, 245))
    d.rounded_rectangle([90, yy + 40, 170, yy + 120], 18, fill=(255, 60, 60, 255))
    d.text((112, yy + 52), "!", font=font("Black", 56), fill=WHITE)
    d.text((200, yy + 36), "SHOP  ·  now", font=font("Bold", 34), fill=(130, 130, 140))
    d.text((200, yy + 80), "NEW DROP! 90% PATI!", font=font("Black", 50), fill=(220, 30, 40))
    d.text((200, yy + 146), "EXCLUSIVE! BUY NOW >>", font=font("Black", 42), fill=(25, 25, 25))
    return overlay(im, L)


def flashback_trans(im, lf, f0, until, t):
    k = lf - f0
    if k < 0 or lf >= until:
        return im
    n = until - f0
    p = k / n
    g = ImageOps.grayscale(im).convert("RGB")
    im = Image.blend(im, g, min(1, p * 1.5))
    # rewind scanlines
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    rnd = random.Random(lf)
    for i in range(14):
        y = rnd.randint(0, H)
        d.rectangle([0, y, W, y + rnd.randint(4, 18)], fill=(255, 255, 255, 60))
    im = overlay(im, L)
    im = Image.blend(im, Image.new("RGB", (W, H), (255, 255, 255)), max(0, p - 0.6) * 2)
    draw_text(im, "◀◀", W / 2, H * 0.40, 120, WHITE, scale=1.0, alpha=min(1, k / 3))
    draw_text(im, t, W / 2, H * 0.52, 74, YELLOW, scale=ease_out_back(k / 6))
    return im


def endcards(lf):
    im = Image.new("RGB", (W, H), (0, 0, 0))
    if lf < 6:
        return im
    k = lf - 6
    a1 = min(1, k / 10)
    draw_text(im, "JANGAN BELI", W / 2, 700, 104, WHITE, alpha=a1, scale=0.9 + 0.1 * ease_out(k / 12), shadow=False)
    draw_text(im, "SEBAB FOMO.", W / 2, 830, 104, YELLOW, alpha=a1, scale=0.9 + 0.1 * ease_out(k / 12), shadow=False)
    if k > 28:
        a2 = min(1, (k - 28) / 10)
        draw_text(im, "KENALI WANGIAN.", W / 2, 1010, 62, WHITE, alpha=a2, weight="ExtraBold", shadow=False)
        draw_text(im, "SEMAK DAKWAAN SELLER.", W / 2, 1090, 62, WHITE, alpha=a2, weight="ExtraBold", shadow=False)
    if k > 70:
        a3 = min(1, (k - 70) / 18)
        d = ImageDraw.Draw(im)
        y = 1460
        d.line([(W / 2 - 160, y - 60), (W / 2 + 160, y - 60)], fill=tuple(int(c * a3) for c in GOLD), width=2)
        draw_text(im, "EXPERIMENTAL PERFUMERY", W / 2, y, 40, tuple(int(c * a3) for c in GOLD), weight="Bold",
                  alpha=1, shadow=False, stroke=0)
    return im


# ------------------------------------------------------------------ claims timing from speech phrases
def phrase_starts(lid, k=3):
    import soundfile as sf
    w, sr = sf.read(os.path.join(ROOT, "voices", lid + ".wav"))
    hop = sr // 30
    e = np.array([np.sqrt(np.mean(w[i:i + hop] ** 2)) for i in range(0, len(w), hop)])
    quiet = e < e.max() * 0.08
    gaps = []
    run = 0
    for i, q in enumerate(quiet):
        if q:
            run += 1
        else:
            if run >= 3:
                gaps.append((run, i))
            run = 0
    gaps = sorted(gaps, reverse=True)[:k - 1]
    return [0] + sorted(g[1] for g in gaps)


# ------------------------------------------------------------------ subtitles
EMPH = ["80%", "PATI", "OWN", "CREATION", "DUPE", "FOMO", "KOTAK", "LIMITED", "EDITION", "EKSKLUSIF", "KILANG",
        "GAME", "MR", "X", "ASTAGAAA!", "CHECKOUT", "SEMAK", "PREMIUM"]
ANGRY = {"s05_mrx_bau", "s05_mrx_habis", "s07_xb_kotak", "s07_xb_dongeng", "s07_xb_mrx", "s09_xb_mrx"}


def wrap(text, f, maxw, d):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def subtitle(im, lf, spec):
    for lid, st, tempo in spec["lines"]:
        ln = int(math.ceil(DUR[lid] / tempo * TL.FPS)) + 8
        k = lf - st
        if 0 <= k < ln:
            text = LINE[lid]["sub"]
            f = font("ExtraBold", 58)
            d = ImageDraw.Draw(im)
            lines = wrap(text, f, 840, d)
            sc = 0.92 + 0.08 * ease_out_back(k / 5)
            y0 = 1395 - (len(lines) - 1) * 40
            for i, line in enumerate(lines):
                # word-level colour: emphasis yellow, anger red
                words = line.split()
                widths = [d.textlength(w + " ", font=f) for w in words]
                x = W / 2 - sum(widths) / 2
                for w_, wd in zip(words, widths):
                    key = w_.strip("!?.,'\"").upper()
                    col = WHITE
                    if any(key.startswith(e.strip("!")) for e in EMPH):
                        col = RED if lid in ANGRY else YELLOW
                    draw_text(im, w_, x + wd / 2 - 8, y0 + i * 80, 58 * sc, col, weight="ExtraBold", stroke=6)
                    x += wd
    return im


def srt():
    starts, total = TL.scene_starts()
    rows = []
    for s in TL.SHOTS:
        for lid, st, tempo in s["lines"]:
            a = (starts[s["id"]] + st) / TL.FPS
            b = a + DUR[lid] / tempo + 0.25
            rows.append((a, b, LINE[lid]["sub"]))
    fmt = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(t * 1000 % 1000):03d}"
    os.makedirs(os.path.join(ROOT, "subtitles"), exist_ok=True)
    with open(os.path.join(ROOT, "subtitles", "MRX_EP01_ms.srt"), "w") as fh:
        for i, (a, b, t) in enumerate(rows, 1):
            fh.write(f"{i}\n{fmt(a)} --> {fmt(b)}\n{t}\n\n")


# ------------------------------------------------------------------ per-shot render
TL_SPEC = {s["id"]: s for s in TL.SHOTS}


def comp_shot(sid):
    spec = TL_SPEC[sid]
    starts, _ = TL.scene_starts()
    g0 = starts[sid]
    fx = spec["fx"]
    claims = None
    for kind, f0, p in fx:
        if kind == "claims":
            claims = [f0 + s for s in phrase_starts(p["line"], len(p["items"]))]
    freeze_ranges = [(f0, p["until"]) for kind, f0, p in fx if kind == "freeze"]
    for lf in range(spec["frames"]):
        out = os.path.join(OUT, f"{g0 + lf:05d}.jpg")
        # which source frame (freeze holds)
        srcf = lf
        frozen = False
        for a, b in freeze_ranges:
            if a <= lf < b:
                srcf, frozen = a - 1, True
        if sid == "end":
            im = endcards(lf)
            im.save(out, quality=93)
            continue
        im = src_frame(sid, srcf, spec)
        # camera-space fx: zoom punch + shake
        zoom, dx, dy = 1.0, 0.0, 0.0
        for kind, f0, p in fx:
            k = lf - f0
            if kind == "zoom_punch" and 0 <= k < 12:
                zoom += p["amt"] * (1 - ease_out(k / 12)) if k > 0 else p["amt"]
            if kind == "zoom_punch" and kind and k >= 12 and sid in ("sh09c",):
                zoom += p["amt"]
            if kind == "shake" and 0 <= k < p["dur"]:
                amp = p["amp"] * 2 * (1 - k / p["dur"])
                r = random.Random(lf * 7 + f0)
                dx += r.uniform(-amp, amp)
                dy += r.uniform(-amp, amp)
        if frozen:
            zoom *= 1.04
        if zoom != 1.0 or dx or dy:
            z = max(zoom, 1.0) + (0.03 if (dx or dy) else 0)
            cw, ch = W / z, H / z
            cx, cy = W / 2 + dx, H / 2 + dy
            im = im.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H),
                                                                                                         Image.BICUBIC)
        warm = 0.6 if spec["scene"] in (2, 3, 4) else 0.0
        im = grade(im, g0 + lf, warm=warm, vig=0.75 if spec["scene"] == 6 else 0.55)
        for kind, f0, p in fx:
            if kind == "black" and f0 <= lf < p["until"]:
                im = Image.new("RGB", (W, H), (0, 0, 0))
            elif kind == "darken" and f0 <= lf < f0 + p["dur"]:
                k = lf - f0
                im = Image.blend(im, ImageChops.multiply(im, Image.new("RGB", (W, H), (150, 120, 190))), min(1, k / 8))
                im = speedlines(im, lf, (60, 30, 90), 40, 90) if k < 30 else im
            elif kind == "sparkles":
                im = sparkles(im, lf, f0, p["dur"])
            elif kind == "lightsweep":
                im = lightsweep(im, lf, f0, p["dur"])
            elif kind == "glint":
                im = glint(im, lf, f0, p["x"], p["y"])
            elif kind == "whiteflash":
                im = flash(im, lf, f0, p["dur"])
            elif kind == "anger":
                im = anger(im, lf, f0, p["dur"])
            elif kind == "shockwave":
                im = shockwave(im, lf, f0, p["x"], p["y"], p["col"])
            elif kind == "impact_frame" and f0 <= lf < f0 + p["dur"]:
                im = impact_frame(im)
            elif kind == "vignette_gold":
                im = Image.blend(im, ImageChops.screen(im, Image.new("RGB", (W, H), (60, 40, 10))), 0.5)
            elif kind == "fomo_meter":
                im = fomo_meter(im, lf, f0, p["dur"])
            elif kind == "label_call":
                im = label_call(im, lf, f0, p["t"], p["dur"])
            elif kind == "inset":
                im = inset(im, lf, f0, p["src"], p["src_start"], p["dur"], p["t"])
            elif kind == "notif":
                im = notif(im, lf, f0, p["dur"])
            elif kind == "freeze" and f0 <= lf < p["until"]:
                k = lf - f0
                if k < 2:
                    im = flash(im, k, 0, 2)
                im = ImageEnhance.Contrast(im).enhance(1.15)
            elif kind == "flashback":
                im = flashback_trans(im, lf, f0, p["until"], p["t"])
        for kind, f0, p in fx:
            if kind == "text_pop":
                im = text_pop(im, lf, f0, p["t"], p["y"], p["col"], p["size"])
            elif kind == "text_stamp":
                im = text_stamp(im, lf, f0, p["t"], p["y"], p["col"], p["size"])
        if claims:
            items = [p for kind, f0, p in fx if kind == "claims"][0]["items"]
            ys = [0.16, 0.24, 0.32]
            cols = [YELLOW, WHITE, YELLOW]
            styles = ["stamp", "pop", "slide"]
            for i, (it, f0) in enumerate(zip(items, claims)):
                k = lf - f0
                if k < 0:
                    continue
                if styles[i] == "stamp":
                    sc = 2.2 - 1.2 * ease_out(k / 4) if k < 4 else 1
                    draw_text(im, it, W / 2, H * ys[i], 104, cols[i], scale=sc, rot=-4)
                elif styles[i] == "pop":
                    draw_text(im, it, W / 2, H * ys[i], 92, cols[i], scale=ease_out_back(k / 7), rot=3)
                else:
                    x = W / 2 + (1 - ease_out(k / 8)) * W
                    draw_text(im, it, x, H * ys[i], 98, RED, rot=-2)
        im = subtitle(im, lf, spec)
        im.save(out, quality=93)
    return sid


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    srt()
    ids = sys.argv[1:] or [s["id"] for s in TL.SHOTS]
    with Pool(int(os.environ.get("JOBS", "2"))) as pool:
        for sid in pool.imap_unordered(comp_shot, ids):
            print("comp", sid, flush=True)
