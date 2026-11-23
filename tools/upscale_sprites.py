"""4x line-art upscale of the extracted Mr X sprites (Real-ESRGAN x4plus anime 6B via spandrel).

The sheets are small (front body 337x760 px, expression heads ~120 px) and a 1080x1920 frame needs
2-4x that. Plain resampling blurs the ink lines; this anime line-art model keeps them crisp without
redrawing the design. The colour pass runs on the sprite's original pixels (incl. the sheet background
around it, kept in the sprite's RGB) and the cut-out mask is scaled separately and re-applied.

  python3 tools/upscale_sprites.py [names...]   -> assets/characters/mrx/sprites_4x/*.png
Weights: RealESRGAN_x4plus_anime_6B.pth (BSD-3, xinntao/Real-ESRGAN), path via MRX_ESRGAN or
~/.cache/mrx-models/.
"""
import os, sys
from pathlib import Path
import numpy as np, torch
from PIL import Image
from scipy import ndimage
from spandrel import ModelLoader

ROOT = Path(__file__).resolve().parents[1] / "assets/characters/mrx"
W = os.environ.get("MRX_ESRGAN", str(Path.home() / ".cache/mrx-models/RealESRGAN_x4plus_anime_6B.pth"))
model = ModelLoader().load_from_file(W).eval()
torch.set_grad_enabled(False)
out_dir = ROOT / "sprites_4x"; out_dir.mkdir(exist_ok=True)
names = sys.argv[1:] or sorted(p.stem for p in (ROOT / "sprites").glob("*.png"))
for n in names:
    im = Image.open(ROOT / f"sprites/{n}.png").convert("RGBA")
    a = np.asarray(im).astype(np.float32) / 255
    x = torch.from_numpy(a[..., :3].transpose(2, 0, 1))[None]
    y = model(x)[0].clamp(0, 1).numpy().transpose(1, 2, 0)
    H, Wd = y.shape[:2]
    al = np.asarray(Image.fromarray((a[..., 3] * 255).astype(np.uint8)).resize((Wd, H), Image.LANCZOS)).astype(np.float32) / 255
    al = np.clip((al - 0.5) * 3 + 0.5, 0, 1)                       # firm the edge back up
    al = ndimage.gaussian_filter(al, 0.8)
    Image.fromarray(np.dstack([y * 255, al * 255]).clip(0, 255).astype(np.uint8), "RGBA").save(out_dir / f"{n}.png")
    print(n, (Wd, H))
