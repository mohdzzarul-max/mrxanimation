// QC helper: bundle once, render stills at given frames, tile into a contact sheet.
// usage: node scripts/stills.mjs <outDir> <frame> [frame...]
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path";
import fs from "node:fs";

const [outDir, ...frames] = process.argv.slice(2);
fs.mkdirSync(outDir, { recursive: true });
const browserExecutable = process.env.REMOTION_BROWSER ?? "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell";
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const composition = await selectComposition({ serveUrl, browserExecutable, id: "ZscentsFinalChapter" });
for (const fr of frames.map(Number)) {
  const output = path.join(outDir, `f${String(fr).padStart(4, "0")}.jpg`);
  await renderStill({ serveUrl, browserExecutable, composition, frame: fr, output, imageFormat: "jpeg", jpegQuality: 85, scale: 0.5 });
  console.log("still", fr);
}
