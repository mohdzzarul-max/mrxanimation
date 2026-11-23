"""Procedural texture generation (PIL). Run once: python3 textures.py
Outputs PNGs into MRX_EP01/textures/.  All branding is fictional."""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "textures")
FONTS = os.path.join(ROOT, "source", "fonts")
os.makedirs(OUT, exist_ok=True)


def F(w, size):
    return ImageFont.truetype(os.path.join(FONTS, f"Montserrat-{w}.ttf"), size)


SKIN = (231, 176, 140)


def mask_front(N=2048):
    """Front projection of MR X's mask (x,z in [-1,1], image right = character's left),
    traced from the front view of the reference sheet. Black base, white markings,
    skin-tone eye openings."""
    im = Image.new("RGB", (N, N), (0, 0, 0))
    d = ImageDraw.Draw(im)
    P = lambda x, z: ((x + 1) / 2 * N, (1 - (z + 1) / 2) * N)
    W = (240, 240, 236)

    def bez(pts, n=40):
        out = []
        for i in range(n + 1):
            t = i / n
            q = list(pts)
            while len(q) > 1:
                q = [((1 - t) * a[0] + t * b[0], (1 - t) * a[1] + t * b[1]) for a, b in zip(q, q[1:])]
            out.append(q[0])
        return out

    def shape(outline, mirror=True):
        for sx in ((1, -1) if mirror else (1,)):
            d.polygon([P(sx * x, z) for x, z in outline], fill=W)

    def stroke(path, w0, w1):
        """Variable-width stroke along a bezier path (tapers from w0 to w1)."""
        c = bez(path, 60)
        L, R_ = [], []
        for i, (x, z) in enumerate(c):
            j = min(i + 1, len(c) - 1); k = max(i - 1, 0)
            dx, dz = c[j][0] - c[k][0], c[j][1] - c[k][1]
            l = math.hypot(dx, dz) + 1e-9
            nx, nz = -dz / l, dx / l
            w = (w0 + (w1 - w0) * i / (len(c) - 1)) / 2
            L.append((x + nx * w, z + nz * w)); R_.append((x - nx * w, z - nz * w))
        return L + R_[::-1]

    # main horn: rises from beside the eye's outer corner, follows the head outline, tip points up
    shape(stroke([(0.50, -0.02), (0.86, 0.10), (0.78, 0.48), (0.42, 0.74)], 0.25, 0.0))
    # inner spike: branches from the horn base, pointing up and inward
    shape(stroke([(0.62, 0.10), (0.48, 0.30), (0.34, 0.42), (0.20, 0.56)], 0.18, 0.0))
    # white band hugging the top-outer rim of the eye, joining the horn base
    shape(stroke([(0.20, 0.06), (0.40, 0.14), (0.58, 0.08), (0.70, -0.10)], 0.07, 0.10))
    # outer cheek bar, curving down and inward
    shape(stroke([(0.74, -0.14), (0.76, -0.32), (0.66, -0.50), (0.56, -0.58)], 0.10, 0.05))
    # inner bracket under the eye: down, step outward, down again (rounded)
    shape(stroke([(0.18, -0.30), (0.17, -0.42), (0.18, -0.50), (0.24, -0.52)], 0.10, 0.10))
    shape(stroke([(0.22, -0.52), (0.30, -0.53), (0.36, -0.54), (0.40, -0.58)], 0.10, 0.10))
    shape(stroke([(0.40, -0.56), (0.41, -0.64), (0.40, -0.70), (0.37, -0.76)], 0.10, 0.03))
    # eye openings (skin), almond tilted slightly down toward the outside
    for sx in (1, -1):
        cx, cz, rx, rz = 0.37 * sx, -0.14, 0.27, 0.18
        pts = []
        for i in range(96):
            a = 2 * math.pi * i / 96
            x = rx * math.cos(a)
            z = rz * math.sin(a) * (1.0 if math.sin(a) > 0 else 0.8)
            z -= 0.04 * (x * sx) / rx
            pts.append(P(cx + x, cz + z))
        d.polygon(pts, fill=SKIN)
    im = im.filter(ImageFilter.GaussianBlur(1.5))
    im.save(os.path.join(OUT, "mrx_mask_front.png"))


def mask_back(N=2048):
    """Back projection (viewed from behind): two large side crescents."""
    im = Image.new("RGB", (N, N), (0, 0, 0))
    d = ImageDraw.Draw(im)
    P = lambda x, z: (int((x + 1) / 2 * N), int((1 - (z + 1) / 2) * N))
    W = (245, 245, 242)
    for sx in (1, -1):
        pts = []
        for i in range(41):
            t = i / 40
            a = math.radians(-60 + 150 * t)
            pts.append((sx * (0.95 * math.cos(a) * 0.9 - 0.02), 0.9 * math.sin(a) * 0.95))
        for i in range(40, -1, -1):
            t = i / 40
            a = math.radians(-60 + 150 * t)
            w = 0.10 * math.sin(math.pi * min(1, t * 1.2))
            pts.append((sx * ((0.95 - w) * math.cos(a) * 0.9 - 0.02 - w * 0.6), (0.9 - w) * math.sin(a) * 0.95))
        d.polygon([P(x, z) for x, z in pts], fill=W)
        # small hook at the bottom
        d.polygon([P(sx * x, z) for x, z in [(0.40, -0.70), (0.55, -0.62), (0.52, -0.55), (0.30, -0.62)]], fill=W)
    im = im.filter(ImageFilter.GaussianBlur(1.2))
    im.save(os.path.join(OUT, "mrx_mask_back.png"))


def brush_x(name="x_brush.png", N=1024, col=(250, 250, 250), seed=1):
    """Dry-brush X emblem with ragged edges and bristle streaks (RGBA)."""
    rnd = random.Random(seed)
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for (x0, y0, x1, y1) in [(0.18, 0.18, 0.82, 0.84), (0.82, 0.16, 0.20, 0.84)]:
        L = math.hypot(x1 - x0, y1 - y0)
        nx, ny = -(y1 - y0) / L, (x1 - x0) / L
        for k in range(70):
            off = (k / 69 - 0.5) * 0.11
            st = rnd.uniform(0.0, 0.07)
            en = rnd.uniform(0.9, 1.0)
            w = rnd.randint(3, 8)
            # gaps in a few bristle lines toward the end = dry brush
            segs = [(st, en)] if rnd.random() > 0.25 else [(st, rnd.uniform(0.5, 0.8))]
            for a, b in segs:
                xa, ya = x0 + (x1 - x0) * a + nx * off, y0 + (y1 - y0) * a + ny * off
                xb, yb = x0 + (x1 - x0) * b + nx * off * 0.6, y0 + (y1 - y0) * b + ny * off * 0.6
                d.line([(xa * N, ya * N), (xb * N, yb * N)], fill=(*col, 255), width=w)
    im = im.filter(ImageFilter.GaussianBlur(0.8))
    im.save(os.path.join(OUT, name))


def label(name, w, h, bg, lines, stripe=None, border=None):
    im = Image.new("RGBA", (w, h), bg)
    d = ImageDraw.Draw(im)
    if stripe:
        d.rectangle([0, int(h * 0.08), w, int(h * 0.2)], fill=stripe)
        d.rectangle([0, int(h * 0.8), w, int(h * 0.92)], fill=stripe)
    if border:
        d.rectangle([8, 8, w - 9, h - 9], outline=border, width=6)
    for (txt, y, size, col, wt) in lines:
        f = F(wt, size)
        tw = d.textlength(txt, font=f)
        d.text(((w - tw) / 2, y * h), txt, font=f, fill=col)
    im.save(os.path.join(OUT, name))


def all_labels():
    GOLD = (222, 176, 82)
    # industrial drum labels (fictional, generic)
    label("drum_label_1.png", 1024, 512, (236, 232, 220, 255), [
        ("READY-MADE", 0.24, 70, (25, 25, 25), "Black"),
        ("FRAGRANCE CONCENTRATE", 0.42, 62, (25, 25, 25), "Black"),
        ("BULK FACTORY SUPPLY  ·  200 L", 0.62, 34, (60, 60, 60), "Bold")], stripe=(230, 120, 20, 255))
    label("drum_label_2.png", 1024, 512, (236, 232, 220, 255), [
        ("BULK FACTORY SUPPLY", 0.28, 66, (25, 25, 25), "Black"),
        ("PRE-MADE FRAGRANCE OIL", 0.47, 56, (25, 25, 25), "Black"),
        ("BATCH 0427-B  ·  NET 200 L", 0.65, 34, (60, 60, 60), "Bold")], stripe=(30, 90, 200, 255))
    label("drum_label_3.png", 1024, 512, (236, 232, 220, 255), [
        ("PRE-MADE", 0.24, 72, (25, 25, 25), "Black"),
        ("FRAGRANCE OIL", 0.42, 72, (25, 25, 25), "Black"),
        ("READY-MADE CONCENTRATE · FACTORY", 0.64, 30, (60, 60, 60), "Bold")], stripe=(230, 120, 20, 255))
    # premium box (fictional brand MAHKOTA)
    label("box_front.png", 768, 1024, (12, 12, 14, 255), [
        ("MAHKOTA", 0.62, 92, GOLD, "Black"),
        ("OWN CREATION", 0.74, 40, GOLD, "Bold"),
        ("EXTRAIT · 80% PATI", 0.81, 34, (200, 160, 80), "Bold"),
        ("LIMITED EDITION", 0.90, 28, (170, 140, 80), "Bold")], border=GOLD)
    # X crest in gold on box
    im = Image.open(os.path.join(OUT, "box_front.png"))
    xb = Image.open(os.path.join(OUT, "x_gold.png")).resize((420, 420))
    im.alpha_composite(xb, (174, 130))
    im.save(os.path.join(OUT, "box_front.png"))
    label("bottle_label.png", 512, 512, (0, 0, 0, 0), [
        ("MAHKOTA", 0.40, 74, GOLD, "Black"),
        ("EXTRAIT", 0.58, 32, (210, 170, 90), "Bold")])
    label("dupe_label.png", 512, 512, (245, 240, 228, 255), [
        ("INSPIRED", 0.30, 64, (40, 40, 40), "Black"),
        ("No. 27", 0.48, 80, (40, 40, 40), "Black"),
        ("50 ml", 0.72, 34, (90, 90, 90), "Bold")], border=(40, 40, 40))
    # booth signage
    label("booth_sign.png", 1600, 400, (10, 10, 12, 255), [
        ("MAHKOTA PARFUM", 0.18, 150, GOLD, "Black"),
        ("OWN CREATION  ·  80% PATI  ·  BUKAN DUPE", 0.64, 60, (235, 205, 140), "Bold")], border=GOLD)
    label("promo_banner.png", 600, 1200, (16, 14, 10, 255), [
        ("80%", 0.18, 210, GOLD, "Black"),
        ("PATI", 0.38, 150, GOLD, "Black"),
        ("LIMITED", 0.62, 92, (240, 225, 190), "Black"),
        ("EDITION", 0.72, 92, (240, 225, 190), "Black")], border=GOLD)
    # phone notification screen
    im = Image.new("RGBA", (540, 1100), (10, 12, 20, 255))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([30, 300, 510, 620], 40, fill=(245, 245, 248, 255))
    d.text((60, 330), "🛍 SHOP · now", font=F("Bold", 30), fill=(120, 120, 130))
    d.text((60, 380), "NEW DROP!", font=F("Black", 64), fill=(220, 30, 40))
    d.text((60, 460), "90% PATI! EXCLUSIVE!", font=F("Black", 38), fill=(20, 20, 20))
    d.text((60, 520), "BUY NOW >>", font=F("Black", 44), fill=(230, 140, 0))
    d.text((150, 120), "21:47", font=F("Bold", 110), fill=(235, 235, 240))
    im.save(os.path.join(OUT, "phone_screen.png"))
    im = Image.new("RGBA", (540, 1100), (8, 10, 16, 255))
    ImageDraw.Draw(im).text((150, 120), "21:47", font=F("Bold", 110), fill=(60, 60, 70))
    im.save(os.path.join(OUT, "phone_off.png"))
    # bedroom poster (MR X logo-ish, fictional)
    im = Image.new("RGBA", (600, 850), (20, 30, 60, 255))
    d = ImageDraw.Draw(im)
    d.text((70, 300), "SNEAKER", font=F("Black", 90), fill=(250, 200, 60))
    d.text((70, 400), "CLUB", font=F("Black", 150), fill=(250, 250, 250))
    d.ellipse([200, 60, 400, 260], outline=(250, 200, 60), width=14)
    im.save(os.path.join(OUT, "poster.png"))
    # holographic perfume icon for X-BOT lesson
    for nm, ok in (("holo_ok.png", True), ("holo_bad.png", False)):
        im = Image.new("RGBA", (512, 640), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        Y = (255, 205, 60, 255)
        d.rounded_rectangle([196, 70, 316, 140], 10, outline=Y, width=10)
        d.rectangle([226, 140, 286, 175], outline=Y, width=8)
        d.rounded_rectangle([126, 175, 386, 470], 30, outline=Y, width=12)
        if ok:
            d.line([(190, 330), (240, 390), (330, 260)], fill=(90, 255, 140, 255), width=22)
            d.text((90, 500), "PATI KILANG = OK", font=F("Black", 40), fill=Y)
        else:
            d.line([(180, 250), (330, 400)], fill=(255, 60, 60, 255), width=24)
            d.line([(330, 250), (180, 400)], fill=(255, 60, 60, 255), width=24)
            d.text((40, 500), "\"OWN CREATION\" PALSU", font=F("Black", 36), fill=(255, 90, 80, 255))
        im.save(os.path.join(OUT, nm))


if __name__ == "__main__":
    mask_front()
    mask_back()
    brush_x()
    brush_x("x_gold.png", col=(226, 182, 90), seed=4)
    brush_x("x_black.png", col=(20, 20, 20), seed=7)
    all_labels()
    print(sorted(os.listdir(OUT)))
