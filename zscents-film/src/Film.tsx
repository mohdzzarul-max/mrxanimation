import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, Sequence, staticFile, useCurrentFrame } from "remotion";
import { AUDIO } from "./config/assets";
import { SCENES, type SceneId } from "./config/timeline";
import { Grain } from "./components/FilmTexture";
import { k } from "./components/anim";
import { loadFonts } from "./components/fonts";
import { S01NasihatAyah } from "./scenes/S01NasihatAyah";
import { S02Termenung } from "./scenes/S02Termenung";
import { S03BilikKayu } from "./scenes/S03BilikKayu";
import { S04TapakPertama } from "./scenes/S04TapakPertama";
import { S05KenalkanPerfume } from "./scenes/S05KenalkanPerfume";
import { S06BoothRamai } from "./scenes/S06BoothRamai";
import { S07Live } from "./scenes/S07Live";
import { S08KoleksiTerakhir } from "./scenes/S08KoleksiTerakhir";
import { S09KematianZscents } from "./scenes/S09KematianZscents";
import { S10KelahiranSemula } from "./scenes/S10KelahiranSemula";

loadFonts();

/** How each scene arrives. Length = the previous scene's `overlapOut`. */
type In = "none" | "dissolve" | "dip" | "flash" | "cut";
const SCENE_MAP: Record<SceneId, { C: React.FC; in: In; label: string }> = {
  "s01-nasihat-ayah": { C: S01NasihatAyah, in: "none", label: "01 Nasihat Ayah" },
  "s02-termenung": { C: S02Termenung, in: "dissolve", label: "02 Termenung" },
  "s03-bilik-kayu": { C: S03BilikKayu, in: "dissolve", label: "03 Bilik Kayu" },
  "s04-tapak-pertama": { C: S04TapakPertama, in: "dip", label: "04 Tapak Pertama" },
  "s05-kenalkan-perfume": { C: S05KenalkanPerfume, in: "dissolve", label: "05 Kenalkan Perfume" },
  "s06-booth-ramai": { C: S06BoothRamai, in: "flash", label: "06 Booth Ramai" },
  "s07-live": { C: S07Live, in: "dissolve", label: "07 LIVE" },
  "s08-koleksi-terakhir": { C: S08KoleksiTerakhir, in: "dip", label: "08 Koleksi Terakhir" },
  "s09-kematian-zscents": { C: S09KematianZscents, in: "dissolve", label: "09 Kematian ZSCENTS" },
  "s10-kelahiran-semula": { C: S10KelahiranSemula, in: "cut", label: "10 Kelahiran Semula" },
};

const SceneShell: React.FC<{
  inMode: In;
  inLen: number;
  duration: number;
  outLen: number;
  dipOut: boolean;
  children: React.ReactNode;
}> = ({ inMode, inLen, duration, outLen, dipOut, children }) => {
  const f = useCurrentFrame();
  let o = 1;
  if (inLen > 0) {
    if (inMode === "dissolve" || inMode === "flash") o = k(f, [0, inLen], [0, 1]);
    if (inMode === "dip") o = k(f, [inLen * 0.5, inLen], [0, 1]);
  }
  if (dipOut && outLen > 0) o *= k(f, [duration, duration + outLen * 0.5], [1, 0]);
  const flash = inMode === "flash" ? k(f, [0, inLen * 0.6, inLen + 8], [0, 0.32, 0]) : 0;
  return (
    <AbsoluteFill style={{ opacity: o }}>
      {children}
      {flash > 0 && (
        <AbsoluteFill style={{ background: "rgb(255,226,180)", opacity: flash, mixBlendMode: "screen" }} />
      )}
    </AbsoluteFill>
  );
};

export const Film: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {SCENES.map((s, i) => {
        const { C, in: inMode, label } = SCENE_MAP[s.id];
        const prev = SCENES[i - 1];
        const next = SCENES[i + 1];
        const nextIn = next ? SCENE_MAP[next.id].in : "none";
        return (
          <Sequence key={s.id} name={label} from={s.from} durationInFrames={s.duration + s.overlapOut}>
            <SceneShell
              inMode={inMode}
              inLen={prev ? prev.overlapOut : 0}
              duration={s.duration}
              outLen={s.overlapOut}
              dipOut={nextIn === "dip"}
            >
              <C />
            </SceneShell>
          </Sequence>
        );
      })}
      <Grain opacity={0.06} />

      {/* Sound: three original stems (+ optional voice-over) */}
      <Audio name="Ambience" src={staticFile(AUDIO.ambience.src)} volume={AUDIO.ambience.volume} />
      <Audio name="Music" src={staticFile(AUDIO.music.src)} volume={AUDIO.music.volume} />
      <Audio name="SFX" src={staticFile(AUDIO.sfx.src)} volume={AUDIO.sfx.volume} />
      {AUDIO.voiceOver && (
        <Audio name="Voice-over" src={staticFile(AUDIO.voiceOver.src)} volume={AUDIO.voiceOver.volume} />
      )}
    </AbsoluteFill>
  );
};
