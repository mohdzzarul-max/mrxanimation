// Render any window.seek(t)/window.DURATION page to MP4 (1080x1920).
//   node tools/render_video.js <page.html> <out.mp4> [--fps 24] [--audio mix.wav] [--stills 0,2.5]
// --stills writes <out>_t<time>.png instead of a video.
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path');
(async () => {
  const a = process.argv.slice(2); const html = path.resolve(a[0]), out = path.resolve(a[1]);
  const opt = k => { const i = a.indexOf(k); return i >= 0 ? a[i + 1] : null; };
  const fps = +(opt('--fps') || 24), audio = opt('--audio'), stills = opt('--stills');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('requestfailed', r => { if (r.url().includes('/assets/products/')) console.warn('note: optional product asset not found: ' + r.url()); else errs.push('missing ' + r.url()); });
  await p.goto('file://' + html + '?capture=1'); await p.waitForFunction(() => window.DURATION > 0, null, { timeout: 60000 });
  const frame = p.locator('#frame');
  if (stills) {
    for (const t of stills.split(',').map(Number)) { await p.evaluate(t => window.seek(t), t); await frame.screenshot({ path: out.replace(/\.mp4$/, '') + `_t${t.toFixed(2)}.png` }); }
  } else {
    const dur = await p.evaluate(() => window.DURATION), n = Math.round(dur * fps);
    const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-',
      ...(audio ? ['-i', audio, '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '192k'] : []),
      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', '-preset', 'slow', '-tune', 'animation', '-t', String(dur), '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const done = new Promise((r, j) => ff.on('close', c => c ? j(new Error('ffmpeg ' + c)) : r()));
    for (let i = 0; i < n; i++) { await p.evaluate(t => window.seek(t), i / fps); const buf = await frame.screenshot({ type: 'png' }); if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r)); }
    ff.stdin.end(); await done; console.log(`✓ ${n} frames → ${path.relative(process.cwd(), out)}`);
  }
  await b.close(); if (errs.length) { console.error(errs); process.exit(1); }
})();
