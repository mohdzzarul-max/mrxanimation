#!/usr/bin/env node
// node intro/render.js [--fps 30] [--out intro/mrx-opening.mp4] [--still 9.5 out.png]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path'); const { pathToFileURL } = require('url');
const a = process.argv.slice(2); const get = (k, d) => (a.includes(k) ? a[a.indexOf(k) + 1] : d);
const fps = +get('--fps', 30), out = get('--out', path.join(__dirname, 'mrx-opening.mp4'));
(async () => {
  const b = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {});
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto(pathToFileURL(path.join(__dirname, 'intro.html')).href + '?capture=1');
  await p.waitForFunction(() => window.seek && window.DURATION);
  await p.evaluate(() => Promise.all([...document.images].map(i => i.decode())));
  if (a.includes('--still')) { // --still t file
    const t = +get('--still'), f = a[a.indexOf('--still') + 2];
    await p.evaluate(t => seek(t), t); await p.screenshot({ path: f }); await b.close(); return;
  }
  const dur = await p.evaluate(() => DURATION), n = Math.round(dur * fps);
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise((r, j) => ff.on('close', c => c ? j(new Error('ffmpeg ' + c)) : r()));
  for (let i = 0; i < n; i++) {
    await p.evaluate(t => seek(t), i / fps);
    const buf = await p.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await done; await b.close();
  if (errs.length) throw new Error(errs.join('|'));
  console.log('done', out);
})();
