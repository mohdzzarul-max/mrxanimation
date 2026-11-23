// Render shot descriptions (JSON) through rig/stage.html to PNG.
//   node tools/render_stills.js episodes/ep01/approval/*.json   -> same name .png next to each json
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const root = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + path.join(root, 'rig/stage.html'));
  await p.waitForFunction(() => window.STAGE_READY);
  for (const f of process.argv.slice(2)) {
    const shot = JSON.parse(fs.readFileSync(f, 'utf8'));
    await p.evaluate(s => window.renderShot(s), shot);
    const out = f.replace(/\.json$/, '.png');
    await p.locator('#stage').screenshot({ path: out });
    console.log('✓', path.relative(process.cwd(), out));
  }
  await b.close(); if (errs.length) { console.error(errs); process.exit(1); }
})();
