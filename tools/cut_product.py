"""Cut the real ZSCENTS product photo out of its white studio background.
Background = near-white pixels connected to the image border (flood fill), so the bottle's own clear
glass highlights inside the outline are kept. Soft 1 px edge. A faint white glass interior stays as
captured in the photo (it is the real product's look on a white sweep).
  python3 tools/cut_product.py assets/products/source/zscents_golden_duke.jpg assets/products/zscents_bottle.png"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
src, out = sys.argv[1], sys.argv[2]
a = np.asarray(Image.open(src).convert("RGB")).astype(float)
lum = a @ [0.299, 0.587, 0.114]; sat = a.max(2) - a.min(2)
bgish = (lum > 238) & (sat < 14)
lab, _ = ndimage.label(bgish)
border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bg = np.isin(lab, list(border))
fg = ndimage.binary_fill_holes(ndimage.binary_opening(~bg, iterations=2))
lab2, n = ndimage.label(fg); sizes = ndimage.sum(fg, lab2, range(1, n + 1)); fg = lab2 == (np.argmax(sizes) + 1)
# the photo's soft floor shadow spills past the glass at the base: clip the bottom rows to the
# bottle's own width (measured just above the base) and drop rows below the glass base line
ys = np.nonzero(fg.any(1))[0]; top, bot = ys.min(), ys.max(); H = bot - top
ref = fg[top + int(.88 * H)]; xs = np.nonzero(ref)[0]; x0, x1 = xs.min(), xs.max()
fg[top + int(.90 * H):, :x0] = False; fg[top + int(.90 * H):, x1 + 1:] = False
cols = fg[:, x0 + 40:x1 - 40]; base = top + int(.90 * H) + np.argmax(cols[top + int(.90 * H):].mean(1) < .5)
if base > top + int(.90 * H): fg[base:] = False
alpha = ndimage.gaussian_filter(fg.astype(float), 0.8)
im = Image.fromarray(np.dstack([a, alpha * 255]).clip(0, 255).astype(np.uint8), "RGBA")
im = im.crop(im.getbbox())
# end the image at the gold base line: last row where the glass spans >= 92% of the width
al = np.asarray(im)[..., 3] > 200; full = np.nonzero(al.mean(1) >= .92)[0]
im = im.crop((0, 0, im.width, int(full.max()) + 3)); im.save(out); print(out, im.size)
