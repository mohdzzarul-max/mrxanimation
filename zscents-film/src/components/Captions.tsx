import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import script from "../config/script.json";
import { ZS_ERA } from "../config/brand";
import type { SceneId } from "../config/timeline";

type Line = { scene: string; start: number; end: number; role: string; text: string };
const LINES = script.lines as Line[];

const FADE = 12;

/**
 * Narration subtitles for one scene. Separate, editable layer: the text lives
 * in src/config/script.json and is also exported as an .srt file.
 */
export const Captions: React.FC<{ scene: SceneId; bottom?: number }> = ({ scene, bottom = 250 }) => {
  const frame = useCurrentFrame();
  const lines = LINES.filter((l) => l.scene === scene);
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {lines.map((l) => {
        if (frame < l.start - 1 || frame > l.end + 1) return null;
        const o = interpolate(frame, [l.start, l.start + FADE, l.end - FADE, l.end], [0, 1, 1, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        const rise = interpolate(frame, [l.start, l.start + 20], [14, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.out(Easing.cubic),
        });
        const blur = interpolate(frame, [l.start, l.start + FADE], [6, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        const father = l.role === "father";
        return (
          <div
            key={`${l.start}-${l.text}`}
            style={{
              position: "absolute",
              left: 90,
              right: 90,
              bottom,
              textAlign: "center",
              opacity: o,
              translate: `0px ${rise}px`,
              filter: `blur(${blur}px)`,
              fontFamily: "Cormorant",
              fontStyle: "italic",
              fontWeight: father ? 500 : 400,
              fontSize: father ? 62 : 58,
              lineHeight: 1.22,
              letterSpacing: 0.3,
              color: father ? "#f3dcb2" : ZS_ERA.cream,
              textShadow: "0 2px 18px rgba(0,0,0,0.85), 0 0 2px rgba(0,0,0,0.7)",
              textWrap: "balance",
            }}
          >
            {l.text}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

/** Small, honest provenance label for AI-reconstructed visuals. */
export const ProvenanceLabel: React.FC<{ text: string; opacity?: number }> = ({ text, opacity = 1 }) => (
  <div
    style={{
      position: "absolute",
      top: 120,
      left: 90,
      fontFamily: "Inter",
      fontWeight: 500,
      fontSize: 22,
      letterSpacing: 4,
      color: "rgba(241,230,210,0.62)",
      opacity,
      padding: "8px 14px",
      border: "1px solid rgba(241,230,210,0.25)",
      borderRadius: 4,
      background: "rgba(0,0,0,0.25)",
    }}
  >
    {text}
  </div>
);
