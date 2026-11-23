import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { ASSETS } from "../config/assets";
import { ZS_ERA } from "../config/brand";
import { Captions } from "../components/Captions";
import { CaptionScrim, Vignette } from "../components/FilmTexture";
import { Glow, Photo } from "../components/Photo";
import { CAM, flicker, k } from "../components/anim";

/** String-light bulbs on the Z Scents banner (image pixels of 04b). */
const STRING_LIGHTS: [number, number][] = [
  ...Array.from({ length: 13 }, (_, i) => [38, 280 + i * 62] as [number, number]),
  ...Array.from({ length: 6 }, (_, i) => [90 + i * 55, 280 + i * 14] as [number, number]),
  ...Array.from({ length: 12 }, (_, i) => [352, 360 + i * 60] as [number, number]),
];

/**
 * 04 — THE STRUGGLE
 * First the empty stall: one bulb, an empty chair, nobody yet.
 * Then the owner at work under string lights. Light is the only thing moving.
 */
export const S04TapakPertama: React.FC = () => {
  const f = useCurrentFrame();
  const b = k(f, [120, 140], [0, 1]);
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {/* A — the empty stall */}
      <Photo
        asset={ASSETS.emptyStall}
        focus={[480, k(f, [0, 140], [900, 860], CAM)]}
        zoom={k(f, [0, 140], [1.07, 1.0], CAM)}
        filter={`${ZS_ERA.grade} brightness(0.95)`}
      >
        <Glow x={535} y={548} r={120} opacity={0.65 * flicker(f, 1, 0.25)} color="255,200,120" />
        <Glow x={535} y={760} r={420} opacity={0.18 * flicker(f, 1, 0.25)} color="255,170,90" />
        <Glow x={665} y={655} r={70} opacity={0.5 * flicker(f, 2, 0.2)} color="255,200,120" />
      </Photo>
      {/* B — the owner arranging bottles */}
      <Photo
        asset={ASSETS.firstStall}
        focus={[k(f, [120, 320], [640, 560], CAM), k(f, [120, 320], [900, 860], CAM)]}
        zoom={k(f, [120, 320], [1.14, 1.03], CAM)}
        filter={ZS_ERA.grade}
        opacity={b}
      >
        {STRING_LIGHTS.map(([x, y], i) => (
          <Glow key={i} x={x} y={y} r={22} opacity={0.55 * flicker(f, i + 10, 0.45)} color="255,215,150" />
        ))}
        <Glow x={560} y={540} r={90} opacity={0.4 * flicker(f, 40, 0.1)} color="255,190,110" />
        {/* warm spill sweeping over the bottles */}
        <Glow x={k(f, [140, 316], [300, 640])} y={1040} r={260} opacity={0.22} color="255,190,120" />
      </Photo>
      <Vignette strength={0.6} />
      <CaptionScrim />
      <Captions scene="s04-tapak-pertama" />
    </AbsoluteFill>
  );
};
