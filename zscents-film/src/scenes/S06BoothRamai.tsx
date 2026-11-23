import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { ASSETS } from "../config/assets";
import { ZS_ERA } from "../config/brand";
import script from "../config/script.json";
import { Captions, ProvenanceLabel } from "../components/Captions";
import { CaptionScrim, Vignette } from "../components/FilmTexture";
import { Glow, Photo } from "../components/Photo";
import { CAM, flicker, k } from "../components/anim";

/** Festoon bulbs across the booth (image pixels). */
const BULBS: [number, number][] = [
  [470, 300], [530, 300], [598, 300], [665, 300], [740, 300], [812, 300], [882, 298], [950, 300],
  [1022, 298], [1088, 298], [1145, 298], [1232, 300], [1300, 296], [1362, 290],
];

type Shot = { from: number; to: number; focus: [[number, number], [number, number]]; zoom: [number, number] };
const SHOTS: Shot[] = [
  { from: 0, to: 68, focus: [[880, 230], [915, 230]], zoom: [1.0, 1.05] }, // branding
  { from: 62, to: 132, focus: [[870, 610], [930, 600]], zoom: [1.28, 1.34] }, // products
  { from: 126, to: 198, focus: [[1300, 560], [1335, 555]], zoom: [1.1, 1.16] }, // chalkboard
  { from: 192, to: 290, focus: [[330, 520], [760, 520]], zoom: [1.04, 1.0] }, // visitors, pan
];
const XF = 6; // dissolve frames between shots

/**
 * 06 — GROWING SUPPORT
 * Tempo lifts: short, smooth cuts between branding, products, the chalkboard
 * and the visitors. Reconstructed image -> labelled on screen.
 */
export const S06BoothRamai: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {SHOTS.map((s, i) => {
        if (f < s.from - 1 || f > s.to + 1) return null;
        const o = i === 0 ? 1 : k(f, [s.from, s.from + XF], [0, 1]);
        return (
          <Photo
            key={i}
            asset={ASSETS.boothCrowd}
            focus={[
              k(f, [s.from, s.to], [s.focus[0][0], s.focus[1][0]], CAM),
              k(f, [s.from, s.to], [s.focus[0][1], s.focus[1][1]], CAM),
            ]}
            zoom={k(f, [s.from, s.to], s.zoom)}
            filter={`${ZS_ERA.grade} brightness(1.04)`}
            opacity={o}
          >
            {BULBS.map(([x, y], j) => (
              <Glow key={j} x={x} y={y} r={26} opacity={0.5 * flicker(f, j + 3, 0.3)} color="255,215,150" />
            ))}
            <Glow x={1305} y={390} r={60} opacity={0.5} color="255,210,140" />
          </Photo>
        );
      })}
      <Vignette strength={0.55} />
      <ProvenanceLabel text={script.titles.reconstructionLabel} opacity={k(f, [8, 20], [0, 1])} />
      <CaptionScrim />
      <Captions scene="s06-booth-ramai" />
    </AbsoluteFill>
  );
};
