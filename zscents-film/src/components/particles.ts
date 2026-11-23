import { useEffect, useState } from "react";
import { continueRender, delayRender, staticFile } from "remotion";
import { ASSETS } from "../config/assets";
import { rand } from "./anim";

/**
 * Deterministic particle system shared by scene 09 (ZSCENTS emblem
 * disintegrates) and scene 10 (the same fragments reorganise into the X).
 * Every position is a pure function of the frame, so renders are repeatable
 * and can be split across machines.
 */

export const ZS_SIZE = 780; // on-screen size of the ZS emblem
export const X_SIZE = 1150; // on-screen size of the full X logo canvas
export const CENTER: [number, number] = [540, 880];
export const PARTICLES = 6500;
const SAMPLE = 627; // sampling resolution of the logos
export const FIELD = 314; // resolution of the disintegration field

export type Particle = {
  sx: number; // source (on ZS emblem), screen px
  sy: number;
  r: number;
  g: number;
  b: number;
  release: number; // 0..1 order in which it breaks away
  vx: number;
  vy: number;
  life: number; // frames
  phase: number;
  size: number;
  tx: number; // target on X emblem, screen px
  ty: number;
  stagger: number;
  swirl: number;
  burst: number;
};

export type LogoData = {
  zsImage: HTMLImageElement;
  field: Float32Array; // FIELD x FIELD release values (0..1, >1 = transparent)
  particles: Particle[];
};

const loadImage = (src: string) =>
  new Promise<HTMLImageElement>((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = staticFile(src);
  });

const pixels = (img: HTMLImageElement, size: number) => {
  const c = document.createElement("canvas");
  c.width = size;
  c.height = size;
  const ctx = c.getContext("2d", { willReadFrequently: true })!;
  ctx.drawImage(img, 0, 0, size, size);
  return ctx.getImageData(0, 0, size, size).data;
};

/** Smooth value noise in [0,1]. */
const vnoise = (x: number, y: number, seed: number) => {
  const xi = Math.floor(x);
  const yi = Math.floor(y);
  const xf = x - xi;
  const yf = y - yi;
  const h = (a: number, b: number) => rand(a * 7349 + b * 1931 + seed * 104729);
  const s = (t: number) => t * t * (3 - 2 * t);
  const a = h(xi, yi);
  const b = h(xi + 1, yi);
  const c = h(xi, yi + 1);
  const d = h(xi + 1, yi + 1);
  return a + (b - a) * s(xf) + (c - a) * s(yf) + (a - b - c + d) * s(xf) * s(yf);
};

/** Release order: the right side of the emblem goes first, with an organic noisy front. */
const releaseAt = (u: number, v: number) => {
  const n =
    0.55 * vnoise(u * 6, v * 6, 1) + 0.3 * vnoise(u * 14, v * 14, 2) + 0.15 * vnoise(u * 32, v * 32, 3);
  const dir = 0.72 * (1 - u) + 0.28 * v;
  return Math.min(1, Math.max(0, 0.62 * dir + 0.38 * n));
};

let cache: Promise<LogoData> | null = null;

const build = async (): Promise<LogoData> => {
  const [zs, xa] = await Promise.all([loadImage(ASSETS.logoZscents.src), loadImage(ASSETS.xEmblemAlpha.src)]);
  const zp = pixels(zs, SAMPLE);
  const xp = pixels(xa, SAMPLE);

  // disintegration field
  const fz = pixels(zs, FIELD);
  const field = new Float32Array(FIELD * FIELD);
  for (let y = 0; y < FIELD; y++)
    for (let x = 0; x < FIELD; x++) {
      const i = y * FIELD + x;
      field[i] = fz[i * 4 + 3] < 8 ? 2 : releaseAt(x / FIELD, y / FIELD);
    }

  // candidate pixels
  const src: number[] = [];
  const tgt: number[] = [];
  for (let i = 0; i < SAMPLE * SAMPLE; i++) {
    if (zp[i * 4 + 3] > 150) src.push(i);
    if (xp[i * 4 + 3] > 110) tgt.push(i);
  }

  const zScale = ZS_SIZE / SAMPLE;
  const xScale = X_SIZE / SAMPLE;
  const particles: Particle[] = [];
  for (let p = 0; p < PARTICLES; p++) {
    const si = src[Math.floor(rand(p * 3 + 1) * src.length)];
    const u = (si % SAMPLE) / SAMPLE;
    const v = Math.floor(si / SAMPLE) / SAMPLE;
    const ti = tgt[Math.floor(rand(p * 3 + 2) * tgt.length)];
    particles.push({
      sx: CENTER[0] - ZS_SIZE / 2 + (si % SAMPLE) * zScale,
      sy: CENTER[1] - ZS_SIZE / 2 + Math.floor(si / SAMPLE) * zScale,
      r: zp[si * 4],
      g: zp[si * 4 + 1],
      b: zp[si * 4 + 2],
      release: releaseAt(u, v),
      vx: -(0.6 + 2.6 * rand(p * 11 + 5)),
      vy: -(0.4 + 1.9 * rand(p * 13 + 7)),
      life: 70 + 60 * rand(p * 17 + 3),
      phase: rand(p * 19 + 9) * Math.PI * 2,
      size: 1.1 + 1.6 * rand(p * 23 + 4) ** 2,
      tx: CENTER[0] - X_SIZE / 2 + (ti % SAMPLE) * xScale + (rand(p * 29) - 0.5) * xScale,
      ty: CENTER[1] - X_SIZE / 2 + Math.floor(ti / SAMPLE) * xScale + (rand(p * 31) - 0.5) * xScale,
      stagger: rand(p * 37 + 1) * 0.3,
      swirl: (rand(p * 41 + 2) - 0.5) * 520,
      burst: rand(p * 43 + 6),
    });
  }
  return { zsImage: zs, field, particles };
};

export const useLogoData = () => {
  const [data, setData] = useState<LogoData | null>(null);
  const [handle] = useState(() => delayRender("Building logo particle data"));
  useEffect(() => {
    if (!cache) cache = build();
    cache
      .then((d) => {
        setData(d);
        continueRender(handle);
      })
      .catch((e) => {
        console.error(e);
        continueRender(handle);
      });
  }, [handle]);
  return data;
};

/** Death: where a particle is `age` frames after breaking away. */
export const deathPosition = (p: Particle, age: number): [number, number] => {
  const a = Math.max(0, age);
  const wind = 0.018 * a * a;
  return [
    p.sx + p.vx * a - wind * 1.1 + 14 * Math.sin(a * 0.06 + p.phase) * Math.min(1, a / 30),
    p.sy + p.vy * a - wind * 0.55 + 10 * Math.cos(a * 0.045 + p.phase * 1.3) * Math.min(1, a / 30),
  ];
};

/** Where every particle rests in the darkness between the two scenes. */
export const scatterPosition = (p: Particle): [number, number] => {
  const [x, y] = deathPosition(p, p.life);
  // fold back into the frame so the rebirth gathers from all around
  const wrap = (v: number, lo: number, hi: number) => lo + ((((v - lo) % (hi - lo)) + (hi - lo)) % (hi - lo));
  return [wrap(x, -60, 1140), wrap(y, 120, 1800)];
};
