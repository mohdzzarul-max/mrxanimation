import React, { useEffect, useRef } from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { ASSETS } from "../config/assets";
import { X_ERA } from "../config/brand";
import script from "../config/script.json";
import { eventFrame } from "../config/timeline";
import { CAM, IN_OUT, OUT, k } from "../components/anim";
import { CENTER, X_SIZE, scatterPosition, useLogoData } from "../components/particles";

const ID = "s10-kelahiran-semula" as const;
/** Centre of the X emblem inside the supplied logo canvas (rows 308-759 of 1254). */
const EMBLEM_CY = 0.425;
const EMBLEM_SCREEN_Y = CENTER[1] + (EMBLEM_CY - 0.5) * X_SIZE;

const easeInOut = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2);

/**
 * 10 — THE REBIRTH
 * Darkness. A faint silver light. The ash of the old emblem gathers and
 * reorganises into the X; on the impact the EXACT supplied emblem is revealed
 * through a radial mask, a metallic light sweeps across it, and only then
 * does the wordmark resolve. Statements, tagline, hold, fade to black.
 */
export const S10KelahiranSemula: React.FC = () => {
  const f = useCurrentFrame();
  const data = useLogoData();
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const light = eventFrame("silverLight", ID);
  const impact = eventFrame("impact", ID);
  const wordmark = eventFrame("wordmarkReveal", ID);
  const st = [eventFrame("statement1", ID), eventFrame("statement2", ID), eventFrame("statement3", ID)];
  const tagline = eventFrame("tagline", ID);
  const fadeOut = eventFrame("fadeOutStart", ID);

  const R0 = light + 22; // particles begin to gather
  const R1 = impact - 4; // ...and lock into the X just before the impact

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !data) return;
    const ctx = canvas.getContext("2d")!;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (f > impact + 40) return;
    const appear = k(f, [light + 4, light + 40], [0, 1]);
    const vanish = k(f, [impact, impact + 32], [1, 0]);
    if (appear * vanish <= 0) return;
    ctx.globalCompositeOperation = "lighter";
    const span = R1 - R0;
    for (const p of data.particles) {
      const [ax, ay] = scatterPosition(p);
      const t = Math.min(1, Math.max(0, ((f - R0) / span - p.stagger) / 0.7));
      const e = easeInOut(t);
      const dx = p.tx - ax;
      const dy = p.ty - ay;
      const len = Math.hypot(dx, dy) || 1;
      const sw = Math.sin(Math.PI * e) * p.swirl;
      let x = ax + dx * e + (-dy / len) * sw;
      let y = ay + dy * e + (dx / len) * sw;
      // gentle pull towards the light before the gathering starts
      const pre = k(f, [light, R0 + 10], [0, 1]) * (1 - e);
      x += (CENTER[0] - x) * 0.04 * pre;
      y += (EMBLEM_SCREEN_Y - y) * 0.04 * pre;
      // impact: a third of the grains are thrown outwards as sparks
      if (f > impact && p.burst < 0.33) {
        const a = f - impact;
        const ox = x - CENTER[0];
        const oy = y - EMBLEM_SCREEN_Y;
        const ol = Math.hypot(ox, oy) || 1;
        const d = 260 * (1 - Math.exp(-a / 14)) * (0.4 + p.burst * 2);
        x += (ox / ol) * d;
        y += (oy / ol) * d;
      }
      const tw = 0.65 + 0.35 * Math.sin(f * 0.4 + p.phase * 3);
      const lock = 0.55 + 0.45 * e;
      const a = appear * (p.burst < 0.33 ? Math.max(0, 1 - (f - impact) / 40) : vanish) * tw * lock;
      if (a <= 0.01) continue;
      const s = p.size * (0.85 + 0.4 * e);
      ctx.fillStyle = `rgba(226,230,238,${a})`;
      ctx.fillRect(x - s / 2, y - s / 2, s, s);
    }
    ctx.globalCompositeOperation = "source-over";
  }, [f, data, light, impact, R0, R1]);

  // logo group moves up once the wordmark has resolved
  const lift = k(f, [wordmark + 48, wordmark + 80], [0, 1], IN_OUT);
  const groupScale = 1 - 0.14 * lift;
  const groupY = -250 * lift;

  const revealR = k(f, [impact - 2, impact + 30], [0, 820], OUT);
  const sweep = k(f, [impact + 30, impact + 68], [-0.3, 1.3], CAM);
  const sweep2 = k(f, [wordmark + 4, wordmark + 44], [-0.3, 1.3], CAM);
  const wordW = k(f, [wordmark, wordmark + 36], [0, 62], OUT);
  const wEdge = Math.min(8, wordW);
  const flash = k(f, [impact - 2, impact, impact + 16], [0, 1, 0]);
  const pointLight = k(f, [light, impact - 6], [0, 1], CAM);
  const statementsOut = k(f, [tagline - 18, tagline - 2], [1, 0]);
  const end = k(f, [fadeOut, fadeOut + 24], [1, 0]);

  const logoBox: React.CSSProperties = {
    position: "absolute",
    left: CENTER[0] - X_SIZE / 2,
    top: CENTER[1] - X_SIZE / 2,
    width: X_SIZE,
    height: X_SIZE,
  };
  const maskOf = (src: string): React.CSSProperties => ({
    maskImage: `url(${staticFile(src)})`,
    WebkitMaskImage: `url(${staticFile(src)})`,
    maskSize: "100% 100%",
    WebkitMaskSize: "100% 100%",
  });

  return (
    <AbsoluteFill style={{ background: X_ERA.black, opacity: end }}>
      {/* the faint silver light in the darkness, later a soft backlight */}
      <div
        style={{
          position: "absolute",
          left: CENTER[0] - 500,
          top: EMBLEM_SCREEN_Y - 500 + groupY,
          width: 1000,
          height: 1000,
          borderRadius: "50%",
          background: `radial-gradient(circle, rgba(225,230,240,${0.55 * pointLight}) 0%, rgba(200,210,225,${0.12 * pointLight}) 12%, rgba(200,210,225,0) 55%)`,
          opacity: f < impact ? 1 : k(f, [impact, impact + 40], [1, 0.35]),
        }}
      />
      <canvas ref={canvasRef} width={1080} height={1920} style={{ position: "absolute", inset: 0 }} />

      <div
        style={{
          position: "absolute",
          inset: 0,
          translate: `0px ${groupY}px`,
          scale: String(groupScale),
          transformOrigin: `${CENTER[0]}px ${CENTER[1]}px`,
          // the group is its own stacking context: blend the whole group
          mixBlendMode: "screen",
        }}
      >
        {/* EXACT supplied emblem, revealed through a soft radial mask */}
        <Img
          src={staticFile(ASSETS.xEmblem.src)}
          style={{
            ...logoBox,
            opacity: f < impact - 2 ? 0 : 1,
            mixBlendMode: "screen",
            maskImage: `radial-gradient(circle at 50% ${EMBLEM_CY * 100}%, #000 ${revealR}px, transparent ${revealR + 140}px)`,
            WebkitMaskImage: `radial-gradient(circle at 50% ${EMBLEM_CY * 100}%, #000 ${revealR}px, transparent ${revealR + 140}px)`,
          }}
        />
        {/* metallic light sweep, clipped to the emblem's own shape */}
        <div
          style={{
            ...logoBox,
            ...maskOf(ASSETS.xEmblemAlpha.src),
            mixBlendMode: "screen",
            background: `linear-gradient(115deg, rgba(255,255,255,0) ${sweep * 100 - 14}%, rgba(255,255,255,0.85) ${sweep * 100}%, rgba(255,255,255,0) ${sweep * 100 + 14}%)`,
          }}
        />
        {/* wordmark only after the X has resolved */}
        <Img
          src={staticFile(ASSETS.xWordmark.src)}
          style={{
            ...logoBox,
            opacity: wordW <= 0 ? 0 : k(f, [wordmark, wordmark + 10], [0, 1]),
            mixBlendMode: "screen",
            maskImage: `linear-gradient(90deg, transparent ${50 - wordW}%, #000 ${50 - wordW + wEdge}%, #000 ${50 + wordW - wEdge}%, transparent ${50 + wordW}%)`,
            WebkitMaskImage: `linear-gradient(90deg, transparent ${50 - wordW}%, #000 ${50 - wordW + wEdge}%, #000 ${50 + wordW - wEdge}%, transparent ${50 + wordW}%)`,
          }}
        />
        <div
          style={{
            ...logoBox,
            ...maskOf(ASSETS.xWordmarkAlpha.src),
            mixBlendMode: "screen",
            background: `linear-gradient(100deg, rgba(255,255,255,0) ${sweep2 * 100 - 10}%, rgba(255,255,255,0.8) ${sweep2 * 100}%, rgba(255,255,255,0) ${sweep2 * 100 + 10}%)`,
          }}
        />
      </div>

      {/* impact bloom */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle 560px at 50% ${EMBLEM_SCREEN_Y}px, rgba(235,240,248,0.9), rgba(235,240,248,0.25) 35%, rgba(235,240,248,0) 100%)`,
          opacity: flash * 0.8,
          mixBlendMode: "screen",
        }}
      />

      {/* NO MORE DUPES. / NO MORE CLONES. / ONLY ORIGINAL CREATIONS. */}
      <AbsoluteFill style={{ alignItems: "center", opacity: statementsOut }}>
        {script.titles.statements.map((line, i) => {
          const t0 = st[i];
          const last = i === script.titles.statements.length - 1;
          return (
            <div
              key={line}
              style={{
                position: "absolute",
                top: 1150 + i * 92,
                width: 960,
                textAlign: "center",
                fontFamily: "Inter",
                fontWeight: last ? 500 : 300,
                fontSize: last ? 50 : 46,
                letterSpacing: last ? 7 : 9,
                color: last ? X_ERA.silver : X_ERA.silverDim,
                opacity: k(f, [t0, t0 + 10], [0, 1]),
                filter: `blur(${k(f, [t0, t0 + 10], [10, 0])}px)`,
                translate: `0px ${k(f, [t0, t0 + 16], [18, 0], OUT)}px`,
              }}
            >
              {line}
            </div>
          );
        })}
      </AbsoluteFill>

      {/* tagline */}
      <AbsoluteFill style={{ alignItems: "center" }}>
        <div
          style={{
            position: "absolute",
            top: 1190,
            width: 920,
            textAlign: "center",
            fontFamily: "Cormorant",
            fontStyle: "italic",
            fontWeight: 500,
            fontSize: 60,
            lineHeight: 1.2,
            color: X_ERA.silver,
            opacity: k(f, [tagline, tagline + 26], [0, 1]),
            letterSpacing: k(f, [tagline, tagline + 80], [4, 1], OUT),
            filter: `blur(${k(f, [tagline, tagline + 20], [8, 0])}px)`,
            textWrap: "balance",
          }}
        >
          {script.titles.tagline}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
