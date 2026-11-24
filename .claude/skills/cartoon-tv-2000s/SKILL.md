---
name: cartoon-tv-2000s
description: Make an original 2D cartoon short in the early-2000s TV look (thick black outlines, flat colours, one hard shadow, angular characters, glowing supernatural effects, night city) and render it to MP4 with effects/render.js. Use for "animation macam Danny Phantom", ghost-hero cartoon, Saturday-morning cartoon style. Original characters only - never copy a real show's characters, logo or scenes.
---

# 2000s TV cartoon, in code

## The look (checklist)
- **Line**: one ink colour `#14101c`, 6-8px at 1080 wide, round joins. Everything gets an outline except glows.
- **Fill**: flat colour + ONE hard shadow shape (no gradients on characters). Gradients only for sky and glows.
- **Shapes**: angular - trapezoid torsos, pointed chins, spiky hair, big expressive eyes.
- **Timing**: characters move "on twos" - quantise their time to 12 fps (`Math.floor(t*12)/12`); camera and glows stay smooth at 30 fps.
- **Supernatural FX**: glow = blurred copy of the silhouette in the glow colour under the inked drawing (`ctx.filter='blur(18px)'`). Transformation = two glowing rings that split apart; between them draw the new form (clip).
- **Comic accents**: "!" pop, POW burst stars, speed-line backgrounds, 2-frame white flash on big hits, short screen shake.
- **Palette**: night purples `#0b0820 #2a1450`, pale moon, warm yellow windows, ONE signature glow colour per hero.

## Pipeline
1. Scene file in `cartoon/<name>.html`: one `<canvas>`, uses `../effects/lib/fx.js` `run({duration, update})`. State must be a pure function of `t`.
2. Draw helpers: `fillStroke(fill)`, `poly(pts)`, part functions (`legs`, `torso`, `arm(angle)`, `head(expr)`), each character as `drawX(x, y, scale, palette, pose)`.
3. Plan 4-6 shots of 2-3 s each; hard cuts between them.
4. Render: `node effects/render.js cartoon/<name>.html` -> `effects/renders/<name>.mp4`.
5. Check 4-5 stills with `?t=` before full render.

Reference build: `cartoon/ghost-x.html`.
