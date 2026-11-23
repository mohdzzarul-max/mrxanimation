import { Easing, interpolate } from "remotion";

/** Cinematic ease (slow in, slow out) used for most camera moves. */
export const CAM = Easing.bezier(0.45, 0, 0.25, 1);
export const OUT = Easing.bezier(0.16, 1, 0.3, 1);
export const IN_OUT = Easing.bezier(0.65, 0, 0.35, 1);

/** Clamped interpolate. */
export const k = (
  frame: number,
  input: number[],
  output: number[],
  easing: (t: number) => number = (t) => t,
) => interpolate(frame, input, output, { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing });

/** Fade window: 0 -> 1 -> 1 -> 0 */
export const fadeWindow = (frame: number, a: number, b: number, c: number, d: number) =>
  interpolate(frame, [a, b, c, d], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

/** Deterministic pseudo-random in [0,1) from an integer seed. */
export const rand = (seed: number) => {
  let t = (seed + 0x6d2b79f5) | 0;
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

/** Smooth flicker for practical lights (bulbs, string lights). */
export const flicker = (frame: number, seed: number, depth = 0.12) =>
  1 -
  depth *
    (0.5 +
      0.5 * Math.sin(frame * 0.37 + seed * 5.1) * Math.sin(frame * 0.113 + seed * 1.7) +
      0.25 * Math.sin(frame * 1.9 + seed * 9.3) * (rand(Math.floor(frame / 3) + seed * 997) > 0.92 ? 1 : 0));
