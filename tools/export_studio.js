// Export the perfume-studio set as two layers for sprite compositing (camera at identity):
//   assets/sets/studio/studio_back.png     wall, arch, shelves, glow (opaque)
//   assets/sets/studio/studio_counter.png  display counter (transparent PNG, goes in front of characters)
// Source of truth for the set: episodes/ep01/scene01/scene01.html (buildBackground).
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const root = path.resolve(__dirname, '..');
  const out = path.join(root, 'assets/sets/studio');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(root, 'episodes/ep01/scene01/scene01.html') + '?capture=1&bg=1&t=0');
  await p.waitForFunction(() => window.DURATION > 0);
  await p.evaluate(() => { document.getElementById('fg').style.display = 'none'; });
  await p.screenshot({ path: path.join(out, 'studio_back.png') });
  await p.evaluate(() => {
    document.getElementById('fg').style.display = ''; document.getElementById('bgCam').style.display = 'none';
    document.documentElement.style.background = 'transparent'; document.body.style.background = 'transparent';
  });
  await p.screenshot({ path: path.join(out, 'studio_counter.png'), omitBackground: true });
  await b.close(); console.log('studio layers →', path.relative(process.cwd(), out));
})();
