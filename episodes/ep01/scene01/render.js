#!/usr/bin/env node
/*
 * Render Episode 01 / Scene 01.
 *
 *   node render.js                 → out/scene01.mp4 (24 fps, 1080x1920, with out/scene01_mix.wav)
 *                                    out/scene01_final_frame.png  (continuity reference for Scene 02)
 *                                    out/bg_plate.png             (empty studio, for reuse)
 *   node render.js --stills 0,3.8,8.4,11.99   only PNG stills to out/stills/
 *
 * Needs Node 18+, ffmpeg and Playwright. Run `python3 mix.py` first if the dialogue changed.
 */
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path');
const { pathToFileURL } = require('url');

const DIR = __dirname, OUT = path.join(DIR, 'out'), FPS = 24, W = 1080, H = 1920;
const HTML = pathToFileURL(path.join(DIR, 'scene01.html')).href;
const args = process.argv.slice(2);

async function open(browser, q = '') {
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto(`${HTML}?capture=1${q}`);
  await page.waitForFunction(() => typeof window.seek === 'function' && window.DURATION > 0);
  return { page, errors };
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {});
  const si = args.indexOf('--stills');
  if (si >= 0) {
    const dir = path.join(OUT, 'stills'); fs.mkdirSync(dir, { recursive: true });
    const { page, errors } = await open(browser);
    for (const t of args[si + 1].split(',').map(Number)) {
      await page.evaluate(t => window.seek(t), t);
      await page.screenshot({ path: path.join(dir, `t${t.toFixed(2)}.png`) });
    }
    if (errors.length) console.error(errors);
    await browser.close(); return;
  }

  const { page, errors } = await open(browser);
  const duration = await page.evaluate(() => window.DURATION);
  const frames = Math.round(duration * FPS);
  const mp4 = path.join(OUT, 'scene01.mp4'), wav = path.join(OUT, 'scene01_mix.wav');
  const audioIn = fs.existsSync(wav) ? ['-i', wav] : [];
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
    ...audioIn, '-map', '0:v', ...(audioIn.length ? ['-map', '1:a', '-c:a', 'aac', '-b:a', '192k'] : []),
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', '-preset', 'slow', '-tune', 'animation',
    '-t', String(duration), '-movflags', '+faststart', mp4], { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise((res, rej) => ff.on('close', c => (c === 0 ? res() : rej(new Error(`ffmpeg exited ${c}`)))));
  let last;
  for (let i = 0; i < frames; i++) {
    await page.evaluate(t => window.seek(t), i / FPS);
    last = await page.screenshot({ type: 'png' });
    if (!ff.stdin.write(last)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 48 === 0) process.stdout.write(`  frame ${i}/${frames}\r`);
  }
  ff.stdin.end(); await done;
  // the exact last frame of the video = first frame of Scene 02
  fs.writeFileSync(path.join(OUT, 'scene01_final_frame.png'), last);
  const bg = await open(browser, '&bg=1');
  await bg.page.evaluate(t => window.seek(t), (frames - 1) / FPS);
  await bg.page.screenshot({ path: path.join(OUT, 'bg_plate.png') });
  await browser.close();
  if (errors.length || bg.errors.length) { console.error('page errors:', errors, bg.errors); process.exit(1); }
  console.log(`✓ ${frames} frames → ${path.relative(process.cwd(), mp4)}`);
})();
