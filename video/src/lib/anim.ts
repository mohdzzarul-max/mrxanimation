import {Easing, interpolate, spring} from 'remotion';
import {FPS} from '../config/timeline';

export const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
// After-Effects-like curves
export const E = {
  out: Easing.bezier(0.16, 1, 0.3, 1), // expo-out: fast impact, soft settle
  inOut: Easing.bezier(0.65, 0, 0.35, 1),
  in: Easing.bezier(0.5, 0, 0.75, 0),
  back: Easing.bezier(0.34, 1.56, 0.64, 1), // overshoot
  snap: Easing.bezier(0.7, 0, 0.2, 1),
  linear: (t: number) => t,
};
/** keyframe interpolate with per-segment easing. kf: [[frame, value], ...] */
export const kf = (f: number, keys: [number, number][], ease: (t: number) => number = E.inOut) =>
  interpolate(f, keys.map((k) => k[0]), keys.map((k) => k[1]), {...clamp, easing: ease});
export const ramp = (f: number, a: number, b: number, ease: (t: number) => number = E.out) =>
  interpolate(f, [a, b], [0, 1], {...clamp, easing: ease});
export const spr = (f: number, delay = 0, cfg: {damping?: number; stiffness?: number; mass?: number} = {}) =>
  spring({frame: f - delay, fps: FPS, config: {damping: 12, stiffness: 140, mass: 0.8, ...cfg}});
/** deterministic pseudo random 0..1 */
export const rnd = (seed: number) => {
  const x = Math.sin(seed * 12.9898 + 78.233) * 43758.5453;
  return x - Math.floor(x);
};
/** smooth deterministic noise (value-noise) for shake / idle drift */
export const noise1 = (t: number, seed = 0) => {
  const i = Math.floor(t);
  const f = t - i;
  const u = f * f * (3 - 2 * f);
  return (rnd(i + seed * 101) * (1 - u) + rnd(i + 1 + seed * 101) * u) * 2 - 1;
};
/** decaying camera shake */
export const shake = (f: number, at: number, amp = 30, dur = 12, seed = 1) => {
  const d = f - at;
  if (d < 0 || d > dur) return {x: 0, y: 0, r: 0};
  const k = Math.pow(1 - d / dur, 2) * amp;
  return {x: noise1(d * 1.7, seed) * k, y: noise1(d * 1.7, seed + 7) * k, r: noise1(d * 1.3, seed + 13) * k * 0.05};
};
/** 0..1 blink curve, ~5 frames, at listed frames (relative) */
export const blink = (f: number, at: number[]) => {
  for (const a of at) {
    const d = f - a;
    if (d >= 0 && d <= 5) return [0.45, 1, 1, 0.6, 0.2, 0][d];
  }
  return 0;
};
/** auto blink schedule (deterministic) */
export const autoBlink = (f: number, seed: number, every = 85) => {
  const at: number[] = [];
  let t = 10 + rnd(seed) * 30;
  while (t < f + 10) {
    at.push(Math.round(t));
    t += every * (0.6 + rnd(seed + t) * 0.8);
  }
  return blink(f, at);
};
/** speech "talk" pulse used to animate characters while a line is spoken */
export const talk = (f: number, from: number, to: number, seed = 0) => {
  if (f < from || f > to) return 0;
  const t = (f - from) / FPS;
  return Math.max(0, Math.sin(t * 13 + seed) * 0.6 + Math.sin(t * 7.3 + seed * 2) * 0.4);
};
export const mix = (a: number, b: number, t: number) => a + (b - a) * t;
