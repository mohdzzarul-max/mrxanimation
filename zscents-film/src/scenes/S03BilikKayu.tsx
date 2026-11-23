import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { ASSETS } from "../config/assets";
import { ZS_ERA } from "../config/brand";
import script from "../config/script.json";
import { Captions } from "../components/Captions";
import { CaptionScrim, Grain, LightLeak, Vignette } from "../components/FilmTexture";
import { Glow, Photo } from "../components/Photo";
import { CAM, OUT, k } from "../components/anim";

/**
 * 03 — THE HUMBLE BEGINNING
 * Wide dolly-in on the wooden room, then documentary inserts (shelf, worktable)
 * cut from inside the same photograph. RM100 set as quiet typography.
 *
 * NOTE: the room photo is currently a low-resolution stand-in (see assets.ts),
 * treated as a soft memory. Drop in the original and it simply gets sharper.
 */
const GRADE = `${ZS_ERA.grade} blur(0.5px)`;

export const S03BilikKayu: React.FC = () => {
  const f = useCurrentFrame();
  const room = ASSETS.woodenRoom;
  const titleIn = k(f, [118, 150], [0, 1], OUT);
  const titleOut = k(f, [286, 300], [1, 0]);
  const title = titleIn * titleOut;
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {/* A — wide, slow dolly-in towards the table */}
      <Photo
        asset={room}
        focus={[k(f, [0, 120], [470, 520], CAM), k(f, [0, 120], [720, 790], CAM)]}
        zoom={k(f, [0, 120], [1.0, 1.12], CAM)}
        filter={GRADE}
      >
        <Glow x={170} y={480} r={260} opacity={0.3} color="255,210,150" />
      </Photo>
      {/* B — insert: the shelf of bottles */}
      <Photo
        asset={room}
        focus={[k(f, [110, 210], [600, 660], CAM), 500]}
        zoom={k(f, [110, 210], [1.85, 1.95])}
        filter={GRADE}
        opacity={k(f, [110, 122], [0, 1]) * k(f, [200, 212], [1, 0])}
      >
        <Glow x={700} y={610} r={90} opacity={0.35 + 0.1 * Math.sin(f / 9)} />
      </Photo>
      {/* C — insert: the worktable */}
      <Photo
        asset={room}
        focus={[k(f, [200, 320], [470, 540], CAM), k(f, [200, 320], [820, 790], CAM)]}
        zoom={k(f, [200, 320], [1.55, 1.68])}
        filter={GRADE}
        opacity={k(f, [200, 212], [0, 1])}
      />
      <Grain opacity={0.08} />
      <LightLeak progress={k(f, [0, 110], [0, 1])} opacity={0.35} from={[-10, 25]} to={[40, 30]} />
      <Vignette strength={0.65} />
      {/* darken behind the title */}
      <AbsoluteFill style={{ background: "rgba(10,6,3,0.55)", opacity: title }} />
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          top: -180,
          opacity: title,
        }}
      >
        <div
          style={{
            fontFamily: "Cormorant",
            fontWeight: 400,
            fontSize: 220,
            fontVariantNumeric: "lining-nums",
            lineHeight: 1,
            color: ZS_ERA.gold,
            letterSpacing: k(f, [118, 200], [36, 10], OUT),
            textShadow: "0 4px 40px rgba(0,0,0,0.6)",
            filter: `blur(${k(f, [118, 140], [8, 0])}px)`,
          }}
        >
          {script.titles.rm100.value}
        </div>
        <div
          style={{
            height: 1,
            marginTop: 26,
            width: k(f, [134, 190], [0, 360], OUT),
            background: `linear-gradient(90deg, transparent, ${ZS_ERA.gold}, transparent)`,
          }}
        />
        <div
          style={{
            marginTop: 26,
            fontFamily: "Inter",
            fontWeight: 400,
            fontSize: 34,
            letterSpacing: 12,
            color: ZS_ERA.cream,
            textShadow: "0 2px 14px rgba(0,0,0,0.95), 0 0 4px rgba(0,0,0,0.9)",
            opacity: k(f, [146, 176], [0, 1]),
          }}
        >
          {script.titles.rm100.label}
        </div>
      </AbsoluteFill>
      <CaptionScrim />
      <Captions scene="s03-bilik-kayu" />
    </AbsoluteFill>
  );
};
