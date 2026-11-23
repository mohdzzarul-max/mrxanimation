import React, { useEffect, useRef } from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { TRANSITION_ERA, ZS_ERA } from "../config/brand";
import script from "../config/script.json";
import { eventFrame } from "../config/timeline";
import { CAM, OUT, k } from "../components/anim";
import { CENTER, FIELD, ZS_SIZE, deathPosition, useLogoData } from "../components/particles";

/** Frame plan (relative to scene start). */
export const S09 = {
  logoIn: [6, 44],
  glint: [52, 92],
  dim: [92, 138],
  death: [138, 246], // disintegration front sweeps 0 -> 1
};

/**
 * 09 — THE DEATH OF ZSCENTS
 * The original emblem, held. The gold dims. It breaks apart from the right
 * along an organic front: each grain glows like an ember, cools to ash and
 * drifts away on the wind into total darkness. Silence. Then the words.
 */
export const S09KematianZscents: React.FC = () => {
  const f = useCurrentFrame();
  const data = useLogoData();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const layerRef = useRef<HTMLCanvasElement | null>(null);
  const maskRef = useRef<HTMLCanvasElement | null>(null);

  const [D0, D1] = S09.death;
  const progress = k(f, [D0, D1], [-0.06, 1.06]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !data) return;
    const ctx = canvas.getContext("2d")!;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!layerRef.current) {
      layerRef.current = document.createElement("canvas");
      layerRef.current.width = ZS_SIZE;
      layerRef.current.height = ZS_SIZE;
      maskRef.current = document.createElement("canvas");
      maskRef.current.width = FIELD;
      maskRef.current.height = FIELD;
    }
    const layer = layerRef.current;
    const lctx = layer.getContext("2d")!;
    const mask = maskRef.current!;
    const mctx = mask.getContext("2d")!;

    // ---------- the emblem itself (dimming, then eaten by the front)
    const appear = k(f, [S09.logoIn[0], S09.logoIn[1]], [0, 1], CAM);
    const bright = k(f, S09.dim, [1.04, 0.62], CAM);
    const sat = k(f, S09.dim, [1.0, 0.38], CAM);
    lctx.globalCompositeOperation = "source-over";
    lctx.clearRect(0, 0, ZS_SIZE, ZS_SIZE);
    if (progress < 1.06) {
      lctx.filter = `brightness(${bright}) saturate(${sat})`;
      lctx.drawImage(data.zsImage, 0, 0, ZS_SIZE, ZS_SIZE);
      lctx.filter = "none";

      // metallic glint across the gold while it is still alive
      const g0 = S09.glint[0];
      const g1 = S09.glint[1];
      if (f > g0 && f < g1) {
        const gx = k(f, [g0, g1], [-0.4, 1.4], CAM) * ZS_SIZE;
        const grad = lctx.createLinearGradient(gx - 160, gx - 260, gx + 160, gx + 60);
        grad.addColorStop(0, "rgba(255,240,200,0)");
        grad.addColorStop(0.5, "rgba(255,240,200,0.55)");
        grad.addColorStop(1, "rgba(255,240,200,0)");
        lctx.globalCompositeOperation = "source-atop";
        lctx.fillStyle = grad;
        lctx.fillRect(0, 0, ZS_SIZE, ZS_SIZE);
      }

      if (progress > -0.06) {
        // visibility mask + ember band from the release field
        const img = mctx.createImageData(FIELD, FIELD);
        const ember = mctx.createImageData(FIELD, FIELD);
        for (let i = 0; i < FIELD * FIELD; i++) {
          const r = data.field[i];
          const d = r - progress;
          img.data[i * 4 + 3] = Math.max(0, Math.min(255, (d / 0.03) * 255));
          const e = Math.max(0, 1 - Math.abs(d - 0.015) / 0.03);
          ember.data[i * 4] = 255;
          ember.data[i * 4 + 1] = 150 + 80 * e;
          ember.data[i * 4 + 2] = 70 + 60 * e;
          ember.data[i * 4 + 3] = r > 1.5 ? 0 : 255 * e * 0.85;
        }
        // ember glow on the remaining edge
        mctx.putImageData(ember, 0, 0);
        lctx.globalCompositeOperation = "source-atop";
        lctx.drawImage(mask, 0, 0, ZS_SIZE, ZS_SIZE);
        // cut away what has already broken off
        mctx.putImageData(img, 0, 0);
        lctx.globalCompositeOperation = "destination-in";
        lctx.drawImage(mask, 0, 0, ZS_SIZE, ZS_SIZE);
      }
      ctx.globalAlpha = appear;
      ctx.drawImage(layer, CENTER[0] - ZS_SIZE / 2, CENTER[1] - ZS_SIZE / 2);
      ctx.globalAlpha = 1;
    }

    // ---------- released grains: ember -> gold -> ash, carried by the wind
    if (progress > -0.06) {
      ctx.globalCompositeOperation = "lighter";
      for (const p of data.particles) {
        const relFrame = D0 + (p.release + 0.06) / 1.12 * (D1 - D0);
        const age = f - relFrame;
        if (age < 0 || age > p.life) continue;
        const t = age / p.life;
        const [x, y] = deathPosition(p, age);
        const emberT = Math.max(0, 1 - age / 10);
        const ash = Math.min(1, t * 1.6);
        const r = p.r * bright * (1 - ash) + 150 * ash + 60 * emberT;
        const g = p.g * bright * (1 - ash) + 146 * ash + 30 * emberT;
        const b = p.b * bright * (1 - ash) + 140 * ash;
        const a = (1 - t) ** 1.4 * 0.95;
        const s = p.size * (1 - 0.45 * t);
        ctx.fillStyle = `rgba(${r | 0},${g | 0},${b | 0},${a})`;
        ctx.fillRect(x - s / 2, y - s / 2, s, s);
      }
      ctx.globalCompositeOperation = "source-over";
    }
  }, [f, data, progress, D0, D1]);

  const tapi = eventFrame("tapiReveal", "s09-kematian-zscents");
  const nama = eventFrame("namaReveal", "s09-kematian-zscents");
  const textOut = k(f, [392, 414], [1, 0]);
  const halo = k(f, [S09.logoIn[0], S09.logoIn[1]], [0, 1]) * k(f, S09.dim, [1, 0.25]) * k(f, [D0, D0 + 60], [1, 0]);

  return (
    <AbsoluteFill style={{ background: ZS_ERA.ink }}>
      {/* warm halo behind the emblem while it lives */}
      <div
        style={{
          position: "absolute",
          left: CENTER[0] - 620,
          top: CENTER[1] - 620,
          width: 1240,
          height: 1240,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(190,130,60,0.28), rgba(190,130,60,0) 62%)",
          opacity: halo,
        }}
      />
      <canvas
        ref={canvasRef}
        width={1080}
        height={1920}
        style={{
          position: "absolute",
          inset: 0,
          scale: String(k(f, [0, D1], [1.0, 1.045], CAM)),
          transformOrigin: `${CENTER[0]}px ${CENTER[1]}px`,
        }}
      />
      <AbsoluteFill style={{ alignItems: "center", opacity: textOut }}>
        <div
          style={{
            position: "absolute",
            top: 780,
            width: 940,
            textAlign: "center",
            fontFamily: "Cormorant",
            fontStyle: "italic",
            fontWeight: 500,
            fontSize: 84,
            letterSpacing: k(f, [tapi, tapi + 90], [12, 4], OUT),
            color: TRANSITION_ERA.text,
            opacity: k(f, [tapi, tapi + 24], [0, 1]),
            filter: `blur(${k(f, [tapi, tapi + 22], [12, 0])}px)`,
          }}
        >
          {script.titles.notTheEnd}
        </div>
        <div
          style={{
            position: "absolute",
            top: 1030,
            width: 900,
            textAlign: "center",
            fontFamily: "Cormorant",
            fontWeight: 500,
            fontSize: 50,
            letterSpacing: 6,
            color: "rgba(216,212,205,0.82)",
            opacity: k(f, [nama, nama + 24], [0, 1]),
            translate: `0px ${k(f, [nama, nama + 30], [14, 0], OUT)}px`,
            textWrap: "balance",
          }}
        >
          {script.titles.onlyAName}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
