import { continueRender, delayRender, staticFile } from "remotion";

/**
 * Fonts are bundled in public/fonts (SIL Open Font License, see OFL-*.txt)
 * so rendering never depends on the network.
 */
const FACES: { family: string; file: string; weight: string; style?: string }[] = [
  { family: "Cormorant", file: "fonts/Cormorant.ttf", weight: "300 700" },
  { family: "Cormorant", file: "fonts/Cormorant-Italic.ttf", weight: "300 700", style: "italic" },
  { family: "Cinzel", file: "fonts/Cinzel.ttf", weight: "400 900" },
  { family: "Inter", file: "fonts/Inter-Light.otf", weight: "300" },
  { family: "Inter", file: "fonts/Inter-Regular.otf", weight: "400" },
  { family: "Inter", file: "fonts/Inter-Medium.otf", weight: "500" },
];

let started = false;

export const loadFonts = () => {
  if (started || typeof document === "undefined") return;
  started = true;
  const handle = delayRender("Loading bundled fonts");
  Promise.all(
    FACES.map((f) => {
      const face = new FontFace(f.family, `url(${staticFile(f.file)})`, {
        weight: f.weight,
        style: f.style ?? "normal",
      });
      return face.load().then((loaded) => {
        document.fonts.add(loaded);
      });
    }),
  )
    .then(() => continueRender(handle))
    .catch((err) => {
      console.error("Font load failed", err);
      continueRender(handle);
    });
};
