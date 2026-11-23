import timeline from "./timeline.json";

export type SceneId =
  | "s01-nasihat-ayah"
  | "s02-termenung"
  | "s03-bilik-kayu"
  | "s04-tapak-pertama"
  | "s05-kenalkan-perfume"
  | "s06-booth-ramai"
  | "s07-live"
  | "s08-koleksi-terakhir"
  | "s09-kematian-zscents"
  | "s10-kelahiran-semula";

export type SceneTiming = {
  id: SceneId;
  from: number;
  duration: number;
  /** frames this scene keeps playing underneath the next one (dissolve length) */
  overlapOut: number;
};

export const FPS = timeline.fps;
export const WIDTH = timeline.width;
export const HEIGHT = timeline.height;
export const SCENES = timeline.scenes as SceneTiming[];
export const EVENTS = timeline.events;

const last = SCENES[SCENES.length - 1];
export const TOTAL_FRAMES = last.from + last.duration;

export const scene = (id: SceneId): SceneTiming => {
  const s = SCENES.find((x) => x.id === id);
  if (!s) throw new Error(`Unknown scene ${id}`);
  return s;
};

/** Absolute seconds (from timeline events) -> frame relative to a scene. */
export const eventFrame = (key: keyof typeof EVENTS, id: SceneId) => {
  const v = EVENTS[key];
  if (typeof v !== "number") throw new Error(`event ${String(key)} is not a time`);
  return Math.round(v * FPS) - scene(id).from;
};
