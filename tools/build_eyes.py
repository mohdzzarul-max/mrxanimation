"""Split Mr X's drawn eyes into rig layers, using only the approved pixels.

Per eye (head-canvas coordinates, from assets/characters/mrx/rig/head_<view>.png):
  sclera   region inside the eye that shows white + iris (from the drawing)
  iris     the drawn iris disc (blue + pupil + highlights), moves for eye direction, clipped to sclera
  plate    the head with that iris lifted out; the hidden sclera behind it is filled with the
           eye's own sclera white (median of its drawn white pixels)
  lid      blink/half-lid: the drawn black upper-lid band, slid down; the skin it uncovers above is the
           eye's own drawn skin colour. Clipped to the drawn eye opening.
Run: python3 tools/build_eyes.py -> rig/eyes.json + rig/head_<view>_plate.png + rig/eyes/<view>_<eye>_*.png
render_head(view, states) composes a head for any eye state (used for stills and checks).
"""
import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

R = Path(__file__).resolve().parents[1] / "assets/characters/mrx"
RIG = R / "rig"; (RIG / "eyes").mkdir(exist_ok=True, parents=True)
EYES = {k: v for k, v in json.loads((R / "rig_eyes.json").read_text()).items() if not k.startswith("_")}

def classify(px):
    r, g, b = [px[..., i].astype(float) for i in range(3)]
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    blue = (b > r + 40) & (b > 120)
    white = (lum > 195) & (np.abs(r - b) < 45) & (np.abs(r - g) < 45)
    skin = (r > 170) & (r > b + 50) & (g > 90) & ~white
    black = lum < 70
    return blue, white, skin, black

def analyse(view, name, box):
    head = np.asarray(Image.open(RIG / f"head_{view}.png").convert("RGBA"))
    x0, y0, x1, y1 = box
    sub = head[y0:y1, x0:x1]
    blue, white, skin, black = classify(sub)
    H, W = blue.shape
    yy, xx = np.mgrid[0:H, 0:W]
    # eye opening: the drawn skin/white/iris shape, closed across the thick lid band
    opening = ndimage.binary_fill_holes(ndimage.binary_closing(skin | white | blue, iterations=16))
    lab, n = ndimage.label(opening)
    if n > 1:
        sizes = ndimage.sum(opening, lab, range(1, n + 1)); opening = lab == (np.argmax(sizes) + 1)
    # lower edge of the drawn black lid band, measured where the band clearly meets white/iris
    pts = []
    for x in range(W):
        col = np.nonzero(opening[:, x])[0]
        if len(col) < 6: continue
        y = col[0]
        while y < col[-1] and not black[y, x]: y += 1          # skip upper skin strip
        start = y
        while y < col[-1] and black[y, x]: y += 1              # through the band
        if y < col[-1] and (white[y, x] or blue[y, x]) and y > start: pts.append((x, y, y - start))
    pts = np.array(pts)
    med = np.median(pts[:, 2]); pts = pts[pts[:, 2] < 1.6 * med]
    coef = np.polyfit(pts[:, 0], pts[:, 1], 2)
    edge = np.polyval(coef, np.arange(W))
    below = yy >= edge[None, :]
    thick = float(med) * 1.25                                # the band's own drawn thickness
    ink = (sub[..., :3].astype(float) @ [0.299, 0.587, 0.114]) < 95
    lidband = ink & opening & ~below & (yy >= edge[None, :] - thick)
    lidband = ndimage.binary_closing(lidband, iterations=2) & opening & ~below
    # iris circle from the blue extent (its top is hidden under the lid)
    ys, xs = np.nonzero(blue & opening & below)
    cx = (xs.min() + xs.max()) / 2; r = (xs.max() - xs.min()) / 2 + 3; cy = ys.max() - r + 3
    disc = (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r
    # sclera = what shows below the lid band: white + iris + pupil (black inside the disc)
    lum = sub[..., :3].astype(float) @ [0.299, 0.587, 0.114]
    shade = (lum > 135) & ~skin                       # the drawn grey lid-shadow on the white
    sc = opening & below & (white | shade | blue | (black & disc))
    sc = ndimage.binary_fill_holes(ndimage.binary_closing(sc, iterations=2)) & opening & below
    lab, n = ndimage.label(sc)
    if n > 1:
        sizes = ndimage.sum(sc, lab, range(1, n + 1)); sc = lab == (np.argmax(sizes) + 1)
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    iris = disc & sc & ~skin & ~(white & (dist > 0.72 * r))      # keep highlights, drop sclera at the rim
    eye_area = opening & (yy >= edge[None, :] - thick)            # lid band + everything below it in the opening
    sclera_white = np.median(sub[white & sc & ~disc][:, :3], axis=0)
    skin_col = np.median(sub[skin & opening & ~below][:, :3], axis=0) if (skin & opening & ~below).any() else np.median(sub[skin & opening][:, :3], axis=0)
    rows = np.nonzero(sc.any(1))[0]
    return dict(box=box, sub=sub, opening=opening, sclera=sc, iris=iris, lidband=lidband, eye_area=eye_area,
                cx=float(cx), cy=float(cy), r=float(r), sclera_white=sclera_white, skin=skin_col,
                sc_top=int(rows.min()), sc_bot=int(rows.max()))

def layer(full_shape, box, rgba):
    out = np.zeros(full_shape, np.uint8); x0, y0, x1, y1 = box; out[y0:y1, x0:x1] = rgba; return out

def build(view):
    head = np.asarray(Image.open(RIG / f"head_{view}.png").convert("RGBA"))
    plate = head.copy(); meta = {}
    for name, box in EYES[view].items():
        e = analyse(view, name, tuple(box))
        x0, y0, x1, y1 = e["box"]
        # iris layer (drawn pixels)
        ir = e["sub"].copy(); ir[..., 3] = np.where(e["iris"], ir[..., 3], 0)
        # complete the hidden part of the disc (under the lid) from the drawn rings: each missing pixel takes
        # the colour at the same radius along the drawn lower rays of this iris (dark rim, blue band, pupil)
        H_, W_ = e["iris"].shape; yy_, xx_ = np.mgrid[0:H_, 0:W_]
        dx_, dy_ = xx_ - e["cx"], yy_ - e["cy"]; rad = np.sqrt(dx_ ** 2 + dy_ ** 2)
        disc = rad <= e["r"]
        hidden = disc & ~e["iris"]
        profile = np.zeros((int(e["r"]) + 2, 3)); count = np.zeros(int(e["r"]) + 2)
        ang = np.degrees(np.arctan2(dy_, dx_))                                  # +90 = straight down
        ray = e["iris"] & (np.abs(ang - 90) < 35)
        hl = (e["sub"][..., :3].astype(float) @ [0.299, 0.587, 0.114]) > 200   # skip highlight dots
        ok = ray & ~hl
        ri = np.round(rad[ok]).astype(int)
        np.add.at(profile, ri, e["sub"][ok][:, :3].astype(float)); np.add.at(count, ri, 1)
        good = count > 0; idx = np.arange(len(count))
        for c in range(3): profile[:, c] = np.interp(idx, idx[good], profile[good, c] / count[good])
        ir[hidden, :3] = profile[np.round(rad[hidden]).astype(int)].astype(np.uint8); ir[hidden, 3] = 255
        Image.fromarray(layer(head.shape, e["box"], ir)).save(RIG / f"eyes/{view}_{name}_iris.png")
        # plate: lift the iris out, back-fill with this eye's sclera white
        sub = plate[y0:y1, x0:x1]
        sub[e["iris"], :3] = e["sclera_white"]
        # sclera mask layer (for clipping) and lid band layer
        m = np.zeros_like(e["sub"]); m[..., :3] = 255; m[..., 3] = np.where(e["sclera"], 255, 0)
        Image.fromarray(layer(head.shape, e["box"], m)).save(RIG / f"eyes/{view}_{name}_sclera_mask.png")
        lb = e["sub"].copy(); lb[..., 3] = np.where(e["lidband"], 255, 0)
        Image.fromarray(layer(head.shape, e["box"], lb)).save(RIG / f"eyes/{view}_{name}_lidband.png")
        op = np.zeros_like(e["sub"]); op[..., :3] = 255; op[..., 3] = np.where(e["eye_area"], 255, 0)
        Image.fromarray(layer(head.shape, e["box"], op)).save(RIG / f"eyes/{view}_{name}_opening_mask.png")
        meta[name] = dict(box=list(box), iris_center=[x0 + e["cx"], y0 + e["cy"]], iris_r=e["r"],
                          sclera_top=y0 + e["sc_top"], sclera_bottom=y0 + e["sc_bot"],
                          sclera_white=[int(v) for v in e["sclera_white"]], skin=[int(v) for v in e["skin"]])
    Image.fromarray(plate).save(RIG / f"head_{view}_plate.png")
    return meta

def render_head(view, states, meta):
    """states: {eye: {'gx': px, 'gy': px, 'lid': 0..1 (0 = as drawn, 1 = shut)}}
    Gaze: the drawn iris slides inside the drawn sclera; the drawn lid band is laid back on top.
    Lid: the drawn lid band slides down column by column to follow the eye's own shape
    (at 1 it sits on the sclera's lower edge); the skin it uncovers is the eye's own skin colour."""
    out = np.asarray(Image.open(RIG / f"head_{view}_plate.png").convert("RGBA")).astype(float)
    for name, m in meta[view].items():
        st = states.get(name, {})
        scl = np.asarray(Image.open(RIG / f"eyes/{view}_{name}_sclera_mask.png"))[..., 3] > 0
        opn = np.asarray(Image.open(RIG / f"eyes/{view}_{name}_opening_mask.png"))[..., 3] > 0
        ir = np.asarray(Image.open(RIG / f"eyes/{view}_{name}_iris.png")).astype(float)
        lb = np.asarray(Image.open(RIG / f"eyes/{view}_{name}_lidband.png")).astype(float)
        dx, dy = int(round(st.get("gx", 0))), int(round(st.get("gy", 0)))
        if dx or dy:
            ir = np.roll(np.roll(ir, dy, 0), dx, 1)
        a = (ir[..., 3:4] / 255.0) * scl[..., None]
        out[..., :3] = out[..., :3] * (1 - a) + ir[..., :3] * a
        lid = float(st.get("lid", 0))
        band = lb[..., 3] > 0
        if lid > 0:
            H, W = scl.shape
            cols = np.nonzero(scl.any(0))[0]
            top = np.full(W, np.nan); bot = np.full(W, np.nan)
            for x in cols:
                ys = np.nonzero(scl[:, x])[0]; top[x], bot[x] = ys.min(), ys.max()
            xs = np.arange(W); valid = ~np.isnan(top)
            top = np.interp(xs, xs[valid], top[valid]); bot = np.interp(xs, xs[valid], bot[valid])
            shift = np.round((bot - top + 4) * lid).astype(int)
            edge = top + shift                       # new lid edge per column
            yy = np.arange(H)[:, None]
            bx = np.nonzero(band.any(0))[0]
            skin_cover = opn & (yy < edge[None, :])
            # lid colour per column = the drawn skin just above the lash band in that column
            head_px = np.asarray(Image.open(RIG / f"head_{view}.png").convert("RGB")).astype(float)
            lum = head_px @ [0.299, 0.587, 0.114]
            xs_ = np.nonzero(skin_cover.any(0))[0]
            cols = np.zeros((len(xs_), 3))
            for i, x in enumerate(xs_):
                ys = np.nonzero(skin_cover[:, x])[0]
                col = np.array(m["skin"], float)
                bt = np.nonzero(band[:, x])[0]
                y = (bt.min() if len(bt) else ys.min()) - 3
                for k in range(y, max(y - 40, 0), -1):
                    px = head_px[k, x]
                    if px[0] > 170 and px[0] > px[2] + 50 and lum[k, x] > 120: col = px; break
                cols[i] = col
            cols = ndimage.gaussian_filter1d(ndimage.median_filter(cols, size=(15, 1)), 6, axis=0)
            for i, x in enumerate(xs_):
                out[skin_cover[:, x], x, :3] = cols[i]
            moved = np.zeros_like(lb)
            for x in bx:
                k = shift[x]
                moved[k:, x] = lb[:H - k, x] if k > 0 else lb[:, x]
            ma = (moved[..., 3:4] / 255.0) * opn[..., None]
            out[..., :3] = out[..., :3] * (1 - ma) + moved[..., :3] * ma
        else:
            ba = (lb[..., 3:4] / 255.0)
            out[..., :3] = out[..., :3] * (1 - ba) + lb[..., :3] * ba
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))

if __name__ == "__main__":
    meta = {v: build(v) for v in EYES}
    (RIG / "eyes.json").write_text(json.dumps(meta, indent=1))
    for v, m in meta.items():
        for n, e in m.items(): print(v, n, "iris", [round(c) for c in e["iris_center"]], "r", round(e["iris_r"]), "sclera", e["sclera_top"], "-", e["sclera_bottom"])
