import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { GRAIN } from "../config/assets";

/** Minimal moving film grain (pre-rendered tiles, cycled every 2 frames). */
export const Grain: React.FC<{ opacity?: number }> = ({ opacity = 0.07 }) => {
  const frame = useCurrentFrame();
  const i = Math.floor(frame / 2) % GRAIN.length;
  return (
    <AbsoluteFill style={{ mixBlendMode: "overlay", opacity, pointerEvents: "none" }}>
      <Img src={staticFile(GRAIN[i])} style={{ width: "100%", height: "100%" }} />
    </AbsoluteFill>
  );
};

export const Vignette: React.FC<{ strength?: number }> = ({ strength = 0.55 }) => (
  <AbsoluteFill
    style={{
      pointerEvents: "none",
      background: `radial-gradient(ellipse 75% 60% at 50% 46%, rgba(0,0,0,0) 45%, rgba(0,0,0,${strength}) 100%)`,
    }}
  />
);

/** Darkens the lower part of the frame so captions stay legible. */
export const CaptionScrim: React.FC<{ opacity?: number }> = ({ opacity = 1 }) => (
  <AbsoluteFill
    style={{
      pointerEvents: "none",
      opacity,
      background:
        "linear-gradient(to bottom, rgba(0,0,0,0) 58%, rgba(0,0,0,0.55) 78%, rgba(0,0,0,0.78) 100%)",
    }}
  />
);

/** Warm cinematic light leak drifting across the frame. */
export const LightLeak: React.FC<{
  progress: number; // 0..1
  opacity?: number;
  color?: string;
  from?: [number, number];
  to?: [number, number];
}> = ({ progress, opacity = 0.5, color = "255,170,90", from = [-20, 30], to = [110, 60] }) => {
  const x = from[0] + (to[0] - from[0]) * progress;
  const y = from[1] + (to[1] - from[1]) * progress;
  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        mixBlendMode: "screen",
        opacity: opacity * Math.sin(Math.PI * Math.min(1, Math.max(0, progress))),
        background: `radial-gradient(ellipse 55% 40% at ${x}% ${y}%, rgba(${color},0.85) 0%, rgba(${color},0.25) 40%, rgba(${color},0) 75%)`,
      }}
    />
  );
};
