import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { ASSETS } from "../config/assets";
import { ZS_ERA } from "../config/brand";
import script from "../config/script.json";
import { Captions } from "../components/Captions";
import { CaptionScrim, Vignette } from "../components/FilmTexture";
import { Glow, Photo } from "../components/Photo";
import { CAM, k } from "../components/anim";

/**
 * 01 — A FATHER'S ADVICE
 * Darkness and ambience first. The photograph "exposes" slowly out of black;
 * a slow push-in, a shadow drifting across the room, the window breathing.
 * No brand yet.
 */
export const S01NasihatAyah: React.FC = () => {
  const f = useCurrentFrame();
  const exposure = k(f, [20, 130], [0.18, 1], CAM);
  const reveal = k(f, [20, 90], [0, 1]);
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <Photo
        asset={ASSETS.fatherAdvice}
        focus={[k(f, [0, 290], [560, 548], CAM), k(f, [0, 290], [760, 690], CAM)]}
        zoom={k(f, [0, 290], [1.0, 1.075], CAM)}
        filter={`${ZS_ERA.grade} brightness(${exposure})`}
        opacity={reveal}
      >
        {/* window light breathing behind the two figures */}
        <Glow x={560} y={420} r={300} opacity={0.22 + 0.06 * Math.sin(f / 22)} />
        {/* warm bounce on the floorboards */}
        <Glow x={520} y={1160} r={260} opacity={0.16 * reveal} color="255,170,90" />
        {/* a soft shadow drifting slowly across the room (curtain / cloud) */}
        <div
          style={{
            position: "absolute",
            top: 0,
            height: 1448,
            width: 700,
            left: k(f, [0, 290], [-600, 900]),
            background:
              "linear-gradient(90deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.28) 45%, rgba(0,0,0,0.28) 55%, rgba(0,0,0,0) 100%)",
            mixBlendMode: "multiply",
          }}
        />
      </Photo>
      <Vignette strength={0.7} />
      <CaptionScrim opacity={k(f, [90, 110], [0, 1])} />
      <Captions scene="s01-nasihat-ayah" />
      {!script.fatherQuoteApproved && (
        <div
          style={{
            position: "absolute",
            bottom: 110,
            width: "100%",
            textAlign: "center",
            fontFamily: "Inter",
            fontSize: 20,
            letterSpacing: 4,
            color: "rgba(241,230,210,0.45)",
            opacity: k(f, [100, 115], [0, 1]) * k(f, [262, 272], [1, 0]),
          }}
        >
          {script.titles.draftMarker}
        </div>
      )}
    </AbsoluteFill>
  );
};
