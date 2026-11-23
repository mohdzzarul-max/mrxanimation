import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { ASSETS } from "../config/assets";
import { ZS_ERA } from "../config/brand";
import { Captions } from "../components/Captions";
import { CaptionScrim, Vignette } from "../components/FilmTexture";
import { Glow, Photo } from "../components/Photo";
import { CAM, k } from "../components/anim";

/**
 * 05 — REACHING PEOPLE
 * Macro on the hands and the bottle, held; then one continuous, unhurried
 * pull-back that reveals the mosque. Humble and human.
 */
export const S05KenalkanPerfume: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <Photo
        asset={ASSETS.mosqueHands}
        focus={[k(f, [0, 110, 210], [640, 660, 730], CAM), k(f, [0, 110, 210], [720, 700, 600], CAM)]}
        zoom={k(f, [0, 110, 210], [1.62, 1.5, 1.0], CAM)}
        filter={`${ZS_ERA.grade} saturate(0.95)`}
      >
        {/* glint travelling across the glass */}
        <Glow x={k(f, [10, 100], [600, 700])} y={k(f, [10, 100], [650, 700])} r={70} opacity={0.4 * k(f, [10, 40, 80, 100], [0, 1, 1, 0])} color="255,240,210" />
        <Glow x={655} y={392} r={60} opacity={0.5} color="255,230,180" />
        <Glow x={912} y={410} r={70} opacity={0.5} color="255,230,180" />
        <Glow x={1150} y={420} r={60} opacity={0.45} color="255,230,180" />
      </Photo>
      <Vignette strength={0.55} />
      <CaptionScrim />
      <Captions scene="s05-kenalkan-perfume" />
    </AbsoluteFill>
  );
};
