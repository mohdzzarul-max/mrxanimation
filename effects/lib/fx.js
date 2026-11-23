/*
 * MR X effects runtime.
 *
 * Every effect is a pure function of time: window.seek(t) puts every element
 * in its state for second t, so render.js can capture frame by frame.
 *
 * URL parameters (all optional):
 *   capture=1                    set by render.js: no live playback, no fit-to-window
 *   t=1.5                        show one still frame (handy for checking a hold frame)
 *   alpha=1                      hide placeholder footage, transparent background (overlay render)
 *   footage=<dir>&footageN=<n>   real footage as JPEG frames <dir>/0001.jpg.. (render.js --footage makes these)
 *   broll=<dir>&brollN=<n>       same, for the inset B-roll clip
 */
(function () {
  const P = new URLSearchParams(location.search);
  const W = 1080, H = 1920, FPS = 30;
  const capture = P.get('capture') === '1';
  const alpha = P.get('alpha') === '1';

  // ---------- maths ----------
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, k) => a + (b - a) * k;
  const prog = (t, start, dur) => clamp((t - start) / dur);
  const ease = {
    linear: x => x,
    out: x => 1 - Math.pow(1 - x, 3),
    in: x => x * x * x,
    inOut: x => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
    outExpo: x => (x >= 1 ? 1 : 1 - Math.pow(2, -10 * x)),
    inExpo: x => (x <= 0 ? 0 : Math.pow(2, 10 * x - 10)),
    // ~5% overshoot
    back: x => { const c1 = 1.0, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); },
    // damped spring, ~6% overshoot, exactly 1 at x>=1
    spring: x => (x >= 1 ? 1 : x <= 0 ? 0 : 1 - Math.exp(-8 * x) * Math.cos(9 * x)),
  };
  // eased progress of a window: k(t, start, dur, 'back')
  const k = (t, start, dur, e = 'out') => ease[e](prog(t, start, dur));
  // deterministic random (mulberry32)
  function rng(seed) {
    return function () {
      seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
      let r = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      r = (r + Math.imul(r ^ (r >>> 7), 61 | r)) ^ r;
      return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
    };
  }

  // ---------- DOM helpers ----------
  const stage = document.getElementById('stage');
  function el(tag, cls, parent = stage, html) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html !== undefined) e.innerHTML = html;
    parent.appendChild(e);
    return e;
  }
  function canvas(parent = stage, z = 0, w = W, h = H) {
    const c = el('canvas', 'layer', parent);
    c.width = w; c.height = h; c.style.zIndex = z;
    return c;
  }

  // ---------- footage: real frames or placeholder ----------
  const frameCache = {};
  function loadFrame(name, t) {
    const dir = P.get(name), n = parseInt(P.get(name + 'N') || '0', 10);
    if (!dir || !n) return Promise.resolve(null);
    const idx = (Math.floor(t * FPS + 1e-6) % n) + 1;
    const src = `${dir}/${String(idx).padStart(4, '0')}.jpg`;
    const c = frameCache[name];
    if (c && c.src === src) return c.promise;
    const img = new Image();
    const promise = new Promise(res => { img.onload = () => res(img); img.onerror = () => res(null); });
    img.src = src;
    frameCache[name] = { src, promise };
    return promise;
  }
  function drawCover(ctx, img, w, h) {
    const s = Math.max(w / img.width, h / img.height);
    const dw = img.width * s, dh = img.height * s;
    ctx.drawImage(img, (w - dw) / 2, (h - dh) / 2, dw, dh);
  }
  const hasFootage = () => !!(P.get('footage') && P.get('footageN'));

  // placeholder "talking head" set: wall, window glow, drifting bokeh
  function drawBackdrop(ctx, t, w = W, h = H) {
    const g = ctx.createLinearGradient(0, 0, 0, h);
    g.addColorStop(0, '#2b303c'); g.addColorStop(1, '#121419');
    ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
    const r = ctx.createRadialGradient(w * 0.8, h * 0.28, 10, w * 0.8, h * 0.28, w * 0.9);
    r.addColorStop(0, 'rgba(255,170,95,0.42)'); r.addColorStop(1, 'rgba(255,170,95,0)');
    ctx.fillStyle = r; ctx.fillRect(0, 0, w, h);
    const rand = rng(7);
    for (let i = 0; i < 16; i++) {
      const x = rand() * w + Math.sin(t * 0.35 + i) * 14, y = rand() * h * 0.65 + Math.cos(t * 0.3 + i) * 10;
      const rad = (30 + rand() * 70) * (w / W);
      ctx.fillStyle = `rgba(255,${180 + Math.floor(rand() * 60)},140,${0.05 + rand() * 0.12})`;
      ctx.beginPath(); ctx.arc(x, y, rad, 0, Math.PI * 2); ctx.fill();
    }
    const v = ctx.createRadialGradient(w / 2, h / 2, h * 0.3, w / 2, h / 2, h * 0.75);
    v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.55)');
    ctx.fillStyle = v; ctx.fillRect(0, 0, w, h);
  }
  // where the placeholder speaker's head is at time t (stage px)
  function head(t) { return { x: W / 2 + Math.sin(t * 1.6) * 6, y: 1000 + Math.sin(t * 2.1) * 3, r: 200 }; }
  // placeholder speaker silhouette with a warm rim light; transparent elsewhere
  function drawSubject(ctx, t, scale = 1) {
    const hd = head(t), cx = hd.x;
    ctx.save();
    ctx.translate(W / 2, H); ctx.scale(scale, scale); ctx.translate(-W / 2, -H);
    const path = new Path2D();
    path.moveTo(cx - 400, H + 40);
    path.bezierCurveTo(cx - 400, 1440, cx - 320, 1300, cx - 120, 1270);
    path.lineTo(cx - 72, 1160); path.lineTo(cx + 72, 1160); path.lineTo(cx + 120, 1270);
    path.bezierCurveTo(cx + 320, 1300, cx + 400, 1440, cx + 400, H + 40);
    path.closePath();
    path.moveTo(cx + 168, hd.y);
    path.ellipse(cx, hd.y, 168, 208, 0, 0, Math.PI * 2);
    // rim light: fill in the rim colour, then the body shifted left, clipped to the shape
    ctx.fillStyle = '#c98a55'; ctx.fill(path);
    ctx.save(); ctx.clip(path); ctx.translate(-9, 3);
    const g = ctx.createLinearGradient(cx - 400, 0, cx + 400, 0);
    g.addColorStop(0, '#0f1219'); g.addColorStop(0.7, '#242b39'); g.addColorStop(1, '#3a3530');
    ctx.fillStyle = g; ctx.fill(path);
    ctx.restore();
    ctx.restore();
  }
  // placeholder B-roll: dusk skyline drifting past
  function drawBroll(ctx, t, w, h) {
    const g = ctx.createLinearGradient(0, 0, 0, h);
    g.addColorStop(0, '#ff8a4c'); g.addColorStop(0.55, '#7a3e6e'); g.addColorStop(1, '#1b1a33');
    ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
    ctx.fillStyle = 'rgba(255,230,180,0.9)';
    ctx.beginPath(); ctx.arc(w * 0.7, h * 0.42, h * 0.11, 0, Math.PI * 2); ctx.fill();
    [[0.45, '#3b2347', 18], [0.62, '#24182f', 40], [0.8, '#120d1c', 80]].forEach(([base, col, speed], li) => {
      const rand = rng(11 + li); ctx.fillStyle = col;
      let x = -((t * speed) % 2000);
      while (x < w + 200) {
        const bw = 40 + rand() * 90, bh = h * (0.12 + rand() * 0.3);
        ctx.fillRect(x, h * base + h * 0.2 - bh, bw, bh + h); x += bw + 6;
      }
    });
  }
  async function drawFootage(ctx, t, name = 'footage', w = ctx.canvas.width, h = ctx.canvas.height) {
    ctx.clearRect(0, 0, w, h);
    const img = await loadFrame(name, t);
    if (img) { drawCover(ctx, img, w, h); return; }
    if (alpha && name === 'footage') return;
    if (name === 'broll') { drawBroll(ctx, t, w, h); return; }
    ctx.save(); ctx.scale(w / W, h / H); drawBackdrop(ctx, t); drawSubject(ctx, t); ctx.restore();
  }

  // Backdrop and speaker on separate layers, so effects can put things between them.
  // Real footage has no cutout, so it all goes on the back layer; returns true when the speaker is separate.
  async function drawScene(backCtx, subjCtx, t) {
    subjCtx && subjCtx.clearRect(0, 0, subjCtx.canvas.width, subjCtx.canvas.height);
    if (hasFootage() || alpha) { await drawFootage(backCtx, t); return false; }
    drawBackdrop(backCtx, t);
    if (subjCtx) drawSubject(subjCtx, t); else drawSubject(backCtx, t);
    return !!subjCtx;
  }

  // ---------- runner ----------
  function run({ duration, update }) {
    window.DURATION = duration;
    let busy = Promise.resolve();
    window.seek = t => (busy = busy.then(() => update(Math.max(0, Math.min(duration, t)))).then(() => document.fonts.ready).then(() => true));
    if (alpha) document.documentElement.classList.add('alpha');
    if (capture) return;
    const fit = () => {
      const s = Math.min(innerWidth / W, innerHeight / H);
      stage.style.transform = `translate(${(innerWidth - W * s) / 2}px, ${(innerHeight - H * s) / 2}px) scale(${s})`;
    };
    fit(); addEventListener('resize', fit);
    if (P.has('t')) { window.seek(parseFloat(P.get('t'))); return; }
    const t0 = performance.now();
    const loop = () => {
      const t = (((performance.now() - t0) / 1000) % (duration + 0.8));
      window.seek(Math.min(t, duration)).then(() => requestAnimationFrame(loop));
    };
    loop();
  }

  window.fx = { W, H, FPS, P, capture, alpha, clamp, lerp, prog, ease, k, rng, el, canvas,
    drawBackdrop, drawSubject, drawBroll, drawFootage, drawScene, hasFootage, head, run };
})();
