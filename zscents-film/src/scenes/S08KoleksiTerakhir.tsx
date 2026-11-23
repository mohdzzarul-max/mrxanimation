import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { ASSETS, BACKPLATES } from "../config/assets";
import { TRANSITION_ERA, ZS_ERA } from "../config/brand";
import script from "../config/script.json";
import { Captions } from "../components/Captions";
import { CaptionScrim, Vignette } from "../components/FilmTexture";
import { Backplate, Glow, Photo } from "../components/Photo";
import { CAM, OUT, k } from "../components/anim";

const BAND_FADE = (side: "top" | "bottom" | "left" | "right", size: number): React.CSSProperties => ({
  position: "absolute",
  [side]: 0,
  ...(side === "top" || side === "bottom"
    ? { left: 0, right: 0, height: size }
    : { top: 0, bottom: 0, width: size }),
  background: `linear-gradient(to ${side}, rgba(0,0,0,0), #000)`,
});

/**
 * 08 — THE FINAL COLLECTION
 * Label close-ups, then a slow pull-back across the last collection while
 * colour drains away. The farewell is re-set as separate typography.
 */
export const S08KoleksiTerakhir: React.FC = () => {
  const f = useCurrentFrame();
  const band = ASSETS.finalCollectionBand;
  const sat = k(f, [110, 250], [1, 0.1]);
  const bright = k(f, [110, 290], [1, 0.72]);
  const grade = `${ZS_ERA.grade} saturate(${sat}) brightness(${bright})`;
  const shots = [
    { a: 0, b: 92, focus: [[715, 470], [735, 470]], zoom: [2.45, 2.28] },
    { a: 86, b: 162, focus: [[350, 480], [372, 480]], zoom: [2.4, 2.3] },
    { a: 156, b: 300, focus: [[640, 470], [640, 380]], zoom: [2.1, 1.22] },
  ];
  const t1 = k(f, [118, 146], [0, 1], OUT);
  const t2 = k(f, [160, 190], [0, 1], OUT);
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <Backplate src={BACKPLATES["08"]} opacity={0.35} filter={`saturate(${sat})`} />
      {shots.map((s, i) => {
        if (f < s.a - 1 || f > s.b + 1) return null;
        return (
          <Photo
            key={i}
            asset={band}
            fit="contain"
            clamp={false}
            anchor={[540, 820]}
            focus={[
              k(f, [s.a, s.b], [s.focus[0][0], s.focus[1][0]], CAM),
              k(f, [s.a, s.b], [s.focus[0][1], s.focus[1][1]], CAM),
            ]}
            zoom={k(f, [s.a, s.b], s.zoom, CAM)}
            filter={grade}
            opacity={i === 0 ? 1 : k(f, [s.a, s.a + 8], [0, 1])}
          >
            <Glow x={k(f, [s.a, s.b], [200, 1100])} y={420} r={160} opacity={0.18 * k(f, [100, 180], [1, 0])} color="255,220,170" />
            <div style={BAND_FADE("bottom", 200)} />
            <div style={BAND_FADE("top", 80)} />
            <div style={BAND_FADE("left", 120)} />
            <div style={BAND_FADE("right", 120)} />
          </Photo>
        );
      })}
      <Vignette strength={0.7} />
      <CaptionScrim opacity={k(f, [0, 10, 100, 118], [1, 1, 1, 0.6])} />
      <Captions scene="s08-koleksi-terakhir" />
      {/* Farewell typography */}
      <AbsoluteFill style={{ alignItems: "center" }}>
        <div
          style={{
            position: "absolute",
            top: 1310,
            width: 920,
            textAlign: "center",
            fontFamily: "Cormorant",
            fontStyle: "italic",
            fontWeight: 600,
            fontSize: 100,
            lineHeight: 1.02,
            letterSpacing: k(f, [118, 200], [10, 3], OUT),
            color: TRANSITION_ERA.text,
            opacity: t1,
            filter: `blur(${k(f, [118, 140], [10, 0])}px)`,
            textShadow: "0 4px 30px rgba(0,0,0,0.9)",
          }}
        >
          {script.titles.finalChapter.split(" ").slice(0, 2).join(" ")}
          <br />
          {script.titles.finalChapter.split(" ").slice(2).join(" ")}
        </div>
        <div
          style={{
            position: "absolute",
            top: 1546,
            height: 2,
            width: k(f, [150, 200], [0, 320], OUT),
            background: "linear-gradient(90deg, transparent, rgba(160,40,40,0.9), transparent)",
          }}
        />
        <div
          style={{
            position: "absolute",
            top: 1580,
            width: 860,
            textAlign: "center",
            fontFamily: "Cormorant",
            fontWeight: 500,
            fontSize: 46,
            lineHeight: 1.25,
            color: "rgba(216,212,205,0.86)",
            opacity: t2,
            translate: `0px ${(1 - t2) * 12}px`,
            textWrap: "balance",
          }}
        >
          {script.titles.gratitude}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
