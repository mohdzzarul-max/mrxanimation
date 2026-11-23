// Master timeline. 30 fps, 1800 frames = 60.000 s. Music is 120 BPM -> 1 beat = 15 frames.
export const FPS = 30;
export const W = 1080;
export const H = 1920;
export const TOTAL = 1800;
export const SCENES = {
  hook: {from: 0, dur: 180}, // 00:00-00:06
  myth: {from: 180, dur: 270}, // 00:06-00:15
  factors: {from: 450, dur: 360}, // 00:15-00:27
  claims: {from: 810, dur: 390}, // 00:27-00:40
  ebook: {from: 1200, dur: 300}, // 00:40-00:50
  cta: {from: 1500, dur: 300}, // 00:50-01:00
} as const;
// Safe area for TikTok / Reels / Shorts UI chrome
export const SAFE = {top: 150, bottom: 1600, left: 60, right: 960};
