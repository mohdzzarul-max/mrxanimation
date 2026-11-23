import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import type { Asset } from "../config/assets";
import { HEIGHT, WIDTH } from "../config/timeline";

/**
 * A photograph placed with a virtual camera.
 *  - `focus`  : point in IMAGE PIXELS that the camera looks at
 *  - `zoom`   : 1 = image just fills the frame (cover) / fits it (contain)
 *  - `anchor` : where on screen the focus point lands (default: centre)
 * With `fit="cover"` the framing is clamped so an image edge never shows.
 * Children are positioned in image-pixel coordinates, so highlights, glows
 * and lifted UI layers stay locked to the photo while the camera moves.
 */
export const Photo: React.FC<{
  asset: Pick<Asset, "src" | "w" | "h">;
  focus?: [number, number];
  zoom?: number;
  fit?: "cover" | "contain";
  anchor?: [number, number];
  filter?: string;
  opacity?: number;
  clamp?: boolean;
  imgStyle?: React.CSSProperties;
  children?: React.ReactNode;
}> = ({
  asset,
  focus,
  zoom = 1,
  fit = "cover",
  anchor = [WIDTH / 2, HEIGHT / 2],
  filter,
  opacity = 1,
  clamp = true,
  imgStyle,
  children,
}) => {
  const { w, h } = asset;
  const base = fit === "cover" ? Math.max(WIDTH / w, HEIGHT / h) : Math.min(WIDTH / w, HEIGHT / h);
  const s = base * zoom;
  const [fx, fy] = focus ?? [w / 2, h / 2];
  let left = anchor[0] - fx * s;
  let top = anchor[1] - fy * s;
  if (clamp && fit === "cover") {
    left = Math.min(0, Math.max(WIDTH - w * s, left));
    top = Math.min(0, Math.max(HEIGHT - h * s, top));
  }
  return (
    <AbsoluteFill style={{ opacity, overflow: "hidden" }}>
      <div
        style={{
          position: "absolute",
          left,
          top,
          width: w,
          height: h,
          transformOrigin: "0 0",
          transform: `scale(${s})`,
        }}
      >
        <Img
          src={staticFile(asset.src)}
          style={{ position: "absolute", inset: 0, width: w, height: h, filter, ...imgStyle }}
        />
        {children}
      </div>
    </AbsoluteFill>
  );
};

/** Blurred, darkened plate that fills the 9:16 frame behind a non-9:16 photo. */
export const Backplate: React.FC<{ src: string; opacity?: number; filter?: string }> = ({
  src,
  opacity = 1,
  filter,
}) => (
  <AbsoluteFill style={{ opacity }}>
    <Img
      src={staticFile(src)}
      style={{ width: "100%", height: "100%", objectFit: "cover", filter }}
    />
  </AbsoluteFill>
);

/** Soft radial light, positioned in image pixels when used inside <Photo>. */
export const Glow: React.FC<{
  x: number;
  y: number;
  r: number;
  color?: string;
  opacity?: number;
  blend?: React.CSSProperties["mixBlendMode"];
}> = ({ x, y, r, color = "255,196,120", opacity = 1, blend = "screen" }) => (
  <div
    style={{
      position: "absolute",
      left: x - r,
      top: y - r,
      width: r * 2,
      height: r * 2,
      borderRadius: "50%",
      background: `radial-gradient(circle, rgba(${color},0.9) 0%, rgba(${color},0.35) 30%, rgba(${color},0) 70%)`,
      opacity,
      mixBlendMode: blend,
      pointerEvents: "none",
    }}
  />
);
