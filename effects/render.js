#!/usr/bin/env node
/*
 * Render MR X effects to video.
 *
 *   node effects/render.js                      render every effect to effects/renders/<name>.mp4
 *   node effects/render.js orbit snap-zoom      render only these
 *   node effects/render.js orbit --footage me.mp4 [--broll city.mp4]
 *                                              use real footage instead of the placeholder speaker
 *   node effects/render.js orbit --alpha        transparent overlay: effects/renders/<name>.webm (VP9 alpha)
 *   node effects/render.js --fps 60 --out dir   other frame rate / output folder
 *
 * Needs Node 18+, ffmpeg on PATH, and Playwright (npm i -D playwright && npx playwright install chromium).
 * Set CHROME_PATH to use another Chromium build.
 */
const { chromium } = require('playwright');
const { spawn, execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { pathToFileURL } = require('url');

const DIR = __dirname;
const W = 1080, H = 1920;

function parseArgs(argv) {
  const o = { names: [], fps: 30, out: path.join(DIR, 'renders'), alpha: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--footage') o.footage = argv[++i];
    else if (a === '--broll') o.broll = argv[++i];
    else if (a === '--fps') o.fps = parseInt(argv[++i], 10);
    else if (a === '--out') o.out = argv[++i];
    else if (a === '--alpha') o.alpha = true;
    else if (a.startsWith('--')) throw new Error(`unknown option ${a}`);
    else o.names.push(a.replace(/\.html$/, ''));
  }
  return o;
}

// Turn a clip into 0001.jpg.. frames that cover 1080x1920 (centre crop) at the render fps.
function extractFrames(file, fps, tag) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), `mrx-${tag}-`));
  execFileSync('ffmpeg', ['-v', 'error', '-i', file, '-t', '20',
    '-vf', `fps=${fps},scale=${W}:${H}:force_original_aspect_ratio=increase,crop=${W}:${H}`,
    '-q:v', '3', path.join(dir, '%04d.jpg')]);
  const n = fs.readdirSync(dir).filter(f => f.endsWith('.jpg')).length;
  if (!n) throw new Error(`no frames extracted from ${file}`);
  return { dir, n };
}

async function renderOne(browser, name, o, media) {
  const file = path.join(DIR, `${name}.html`);
  if (!fs.existsSync(file)) throw new Error(`no effect called ${name} (${file})`);
  const q = new URLSearchParams({ capture: '1' });
  if (o.alpha) q.set('alpha', '1');
  for (const [k, m] of Object.entries(media)) { q.set(k, pathToFileURL(m.dir).href); q.set(k + 'N', String(m.n)); }
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto(pathToFileURL(file).href + '?' + q.toString());
  await page.waitForFunction(() => typeof window.seek === 'function' && window.DURATION > 0);
  const duration = await page.evaluate(() => window.DURATION);
  const frames = Math.round(duration * o.fps);
  const ext = o.alpha ? 'webm' : 'mp4';
  const outFile = path.join(o.out, `${name}.${ext}`);
  const enc = o.alpha
    ? ['-c:v', 'libvpx-vp9', '-pix_fmt', 'yuva420p', '-b:v', '0', '-crf', '30', '-row-mt', '1']
    : ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-movflags', '+faststart'];
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(o.fps),
    '-c:v', o.alpha ? 'png' : 'mjpeg', '-i', '-', ...enc, outFile], { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise((res, rej) => ff.on('close', c => (c === 0 ? res() : rej(new Error(`ffmpeg exited ${c}`)))));
  const t0 = Date.now();
  for (let i = 0; i < frames; i++) {
    await page.evaluate(t => window.seek(t), i / o.fps);
    const buf = await page.screenshot(o.alpha ? { type: 'png', omitBackground: true } : { type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await done;
  await page.close();
  if (errors.length) throw new Error(`${name}: page errors: ${errors.join(' | ')}`);
  console.log(`✓ ${name}  ${duration}s  ${frames} frames  ${((Date.now() - t0) / 1000).toFixed(1)}s  → ${path.relative(process.cwd(), outFile)}`);
}

(async () => {
  const o = parseArgs(process.argv.slice(2));
  const all = fs.readdirSync(DIR).filter(f => f.endsWith('.html')).map(f => f.slice(0, -5)).sort();
  const names = o.names.length ? o.names : all;
  fs.mkdirSync(o.out, { recursive: true });
  const media = {};
  if (o.footage) media.footage = extractFrames(o.footage, o.fps, 'footage');
  if (o.broll) media.broll = extractFrames(o.broll, o.fps, 'broll');
  const browser = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {});
  let failed = 0;
  for (const n of names) {
    try { await renderOne(browser, n, o, media); } catch (e) { failed++; console.error(`✗ ${n}: ${e.message}`); }
  }
  await browser.close();
  for (const m of Object.values(media)) fs.rmSync(m.dir, { recursive: true, force: true });
  process.exit(failed ? 1 : 0);
})();
