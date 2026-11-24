#!/usr/bin/env node
// Capture still frames and an 8-pose contact sheet.
//   node its-x/stills.js [out.png] [t1 t2 ...]
const { chromium } = require('playwright');
const path = require('path'); const { pathToFileURL } = require('url');
const out = process.argv[2] || path.join(__dirname, 'OUTPUT/8_KEY_POSES_CONTACT_SHEET.png');
const times = process.argv.slice(3).map(Number);
const T = times.length ? times : [0.5, 1.58, 1.9, 2.55, 2.88, 3.2, 3.84, 4.6];
const LABEL = ['Focus on the pipette', 'Tilt + squeeze', 'Drop falls', 'Odd pulse - notices', 'Blink', 'One eyebrow up', 'Surprise: half-step back', 'Settle (hold)'];
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto(pathToFileURL(path.join(__dirname, 'scientist-test.html')).href + '?capture=1');
  await p.waitForFunction(() => typeof window.seek === 'function');
  const shots = [];
  for (const t of T) { await p.evaluate(t => window.seek(t), t); shots.push((await p.screenshot({ type: 'jpeg', quality: 90 })).toString('base64')); }
  const cols = 4, w = 480, h = 270, rows = Math.ceil(T.length / cols);
  const html = `<body style="margin:0;background:#120f18;font:600 15px Inter,sans-serif;color:#eee">
    <div style="display:grid;grid-template-columns:repeat(${cols},${w}px);gap:8px;padding:8px">
    ${shots.map((s, i) => `<div><img src="data:image/jpeg;base64,${s}" width="${w}" height="${h}" style="display:block"><div style="padding:4px 2px">${i + 1}. t=${T[i].toFixed(2)}s (song ${(35.74 + T[i]).toFixed(2)}s)${times.length ? '' : ' · ' + LABEL[i]}</div></div>`).join('')}
    </div></body>`;
  const q = await b.newPage({ viewport: { width: cols * (w + 8) + 8, height: rows * (h + 34) + 8 } });
  await q.setContent(html); await q.screenshot({ path: out, fullPage: true });
  await b.close(); console.log('wrote', out);
})();
