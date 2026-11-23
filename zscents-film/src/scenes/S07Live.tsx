import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { ASSETS, BACKPLATES, LIVE_LAYERS } from "../config/assets";
import script from "../config/script.json";
import { Captions, ProvenanceLabel } from "../components/Captions";
import { Backplate, Glow, Photo } from "../components/Photo";
import { CaptionScrim, Vignette } from "../components/FilmTexture";
import { CAM, OUT, k } from "../components/anim";

/** Timing — mirrored in scripts/generate_audio.py (UI ticks). */
const COMMENT_START = 66; // 2.2 s
const COMMENT_EVERY = 22;
const PURCHASE_START = 90; // 3.0 s
const PURCHASE_EVERY = 16;

/**
 * 07 — THE DIGITAL BREAKTHROUGH
 * The screenshot is split into layers: a clean base plate, then each comment
 * and each purchase row animated in individually (with UI sound). The camera
 * starts on the host and pulls back to reveal the live interface.
 * All numbers/purchases are AI-illustrative -> labelled on screen.
 */
export const S07Live: React.FC = () => {
  const f = useCurrentFrame();
  const live = ASSETS.live;
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <Backplate src={BACKPLATES["07"]} />
      <Photo
        asset={live}
        fit="contain"
        anchor={[540, 900]}
        focus={[k(f, [0, 120], [600, 600], CAM), k(f, [0, 120], [520, 656], CAM)]}
        zoom={k(f, [0, 120, 320], [1.55, 1.0, 0.97], CAM)}
        clamp={false}
        filter="contrast(1.04) saturate(0.95)"
        imgStyle={{ borderRadius: 6, boxShadow: "0 30px 80px rgba(0,0,0,0.6)" }}
      >
        {/* LIVE badge pulse */}
        <Glow x={1078} y={137} r={90} opacity={0.25 + 0.2 * Math.max(0, Math.sin(f / 6))} color="255,60,90" />
        {LIVE_LAYERS.comments.map((c, i) => {
          const t0 = COMMENT_START + i * COMMENT_EVERY;
          const [x0, y0, x1, y1] = c.box;
          const o = k(f, [t0, t0 + 8], [0, 1]);
          return (
            <Img
              key={c.src}
              src={staticFile(c.src)}
              style={{
                position: "absolute",
                left: x0,
                top: y0,
                width: x1 - x0,
                height: y1 - y0,
                opacity: o,
                translate: `0px ${k(f, [t0, t0 + 12], [26, 0], OUT)}px`,
              }}
            />
          );
        })}
        {LIVE_LAYERS.purchases.map((p, i) => {
          const t0 = PURCHASE_START + i * PURCHASE_EVERY;
          const [x0, y0, x1, y1] = p.box;
          return (
            <Img
              key={p.src}
              src={staticFile(p.src)}
              style={{
                position: "absolute",
                left: x0,
                top: y0,
                width: x1 - x0,
                height: y1 - y0,
                opacity: k(f, [t0, t0 + 6], [0, 1]),
                translate: `${k(f, [t0, t0 + 10], [60, 0], OUT)}px 0px`,
                scale: String(k(f, [t0, t0 + 10], [0.96, 1], OUT)),
              }}
            />
          );
        })}
      </Photo>
      <Vignette strength={0.45} />
      <ProvenanceLabel text={script.titles.liveDisclaimer} opacity={k(f, [10, 22], [0, 1])} />
      <CaptionScrim />
      <Captions scene="s07-live" bottom={200} />
    </AbsoluteFill>
  );
};
