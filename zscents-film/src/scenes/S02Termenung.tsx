import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { ASSETS } from "../config/assets";
import { ZS_ERA } from "../config/brand";
import { Captions } from "../components/Captions";
import { CaptionScrim, LightLeak, Vignette } from "../components/FilmTexture";
import { Glow, Photo } from "../components/Photo";
import { CAM, k } from "../components/anim";

/**
 * 02 — REFLECTION
 * Let the image breathe: an almost-still hold, the sun pulsing gently,
 * heat haze drifting. Framing changes are tiny and slow.
 */
export const S02Termenung: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <Photo
        asset={ASSETS.reflection}
        focus={[k(f, [0, 270], [650, 670], CAM), k(f, [0, 270], [720, 700], CAM)]}
        zoom={k(f, [0, 270], [1.0, 1.035], CAM)}
        filter={ZS_ERA.grade}
      >
        <Glow x={945} y={682} r={150 + 8 * Math.sin(f / 18)} opacity={0.55} color="255,190,110" />
        <Glow x={945} y={682} r={420} opacity={0.18 + 0.04 * Math.sin(f / 31)} color="255,140,70" />
        {/* warm haze drifting with the wind */}
        <div
          style={{
            position: "absolute",
            left: k(f, [0, 270], [520, 600]),
            top: 380,
            width: 700,
            height: 700,
            borderRadius: "50%",
            background: "radial-gradient(circle, rgba(255,160,90,0.16), rgba(255,160,90,0) 65%)",
            mixBlendMode: "screen",
          }}
        />
      </Photo>
      <LightLeak progress={k(f, [0, 270], [0, 1])} opacity={0.22} from={[105, 35]} to={[60, 45]} />
      <Vignette strength={0.6} />
      <CaptionScrim />
      <Captions scene="s02-termenung" />
    </AbsoluteFill>
  );
};
