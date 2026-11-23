import React from 'react';
import {C} from '../config/brand';
import {rnd} from '../lib/anim';

/**
 * Comic panel engine: arbitrary polygon panel with masked content, inked border that draws on,
 * hard offset shadow, and reveal modes (iris from centre, wipe, or scale-pop).
 */
export type Pt = [number, number];
export const rectPts = (x: number, y: number, w: number, h: number, skew = 0): Pt[] => [
  [x + skew, y],
  [x + w + skew, y],
  [x + w - skew, y + h],
  [x - skew, y + h],
];

const centroid = (p: Pt[]): Pt => [p.reduce((a, q) => a + q[0], 0) / p.length, p.reduce((a, q) => a + q[1], 0) / p.length];
const perim = (p: Pt[]) => p.reduce((a, q, i) => a + Math.hypot(p[(i + 1) % p.length][0] - q[0], p[(i + 1) % p.length][1] - q[1]), 0);

export type PanelProps = {
  pts: Pt[];
  reveal?: number; // 0..1 content reveal
  border?: number; // 0..1 border draw-on
  mode?: 'iris' | 'wipeL' | 'wipeR' | 'wipeD' | 'wipeU' | 'pop';
  bw?: number;
  borderColor?: string;
  bg?: string;
  shadow?: number; // px offset
  highlight?: number; // 0..1 amber glow border
  dim?: number; // 0..1 darken content
  style?: React.CSSProperties;
  children?: React.ReactNode;
};

export const ComicPanel: React.FC<PanelProps> = ({
  pts, reveal = 1, border = 1, mode = 'iris', bw = 10, borderColor = C.paper, bg = C.charcoal, shadow = 16, highlight = 0, dim = 0, style, children,
}) => {
  const [cx, cy] = centroid(pts);
  const xs = pts.map((p) => p[0]);
  const ys = pts.map((p) => p[1]);
  const minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys);
  let shown = pts;
  if (mode === 'iris' || mode === 'pop') {
    const k = mode === 'pop' ? 0.6 + 0.4 * reveal : reveal;
    shown = pts.map(([x, y]) => [cx + (x - cx) * k, cy + (y - cy) * k] as Pt);
  }
  const poly = (p: Pt[]) => `polygon(${p.map((q) => `${q[0]}px ${q[1]}px`).join(',')})`;
  let clip = poly(shown);
  if (mode.startsWith('wipe')) {
    const r = reveal;
    const box: Pt[] =
      mode === 'wipeL'
        ? [[minX - 50, minY - 50], [minX - 50 + (maxX - minX + 100) * r, minY - 50], [minX - 50 + (maxX - minX + 100) * r - 80, maxY + 50], [minX - 50, maxY + 50]]
        : mode === 'wipeR'
          ? [[maxX + 50 - (maxX - minX + 100) * r, minY - 50], [maxX + 50, minY - 50], [maxX + 50, maxY + 50], [maxX + 50 - (maxX - minX + 100) * r + 80, maxY + 50]]
          : mode === 'wipeD'
            ? [[minX - 50, minY - 50], [maxX + 50, minY - 50], [maxX + 50, minY - 50 + (maxY - minY + 100) * r], [minX - 50, minY - 50 + (maxY - minY + 100) * r - 60]]
            : [[minX - 50, maxY + 50 - (maxY - minY + 100) * r], [maxX + 50, maxY + 50 - (maxY - minY + 100) * r + 60], [maxX + 50, maxY + 50], [minX - 50, maxY + 50]];
    clip = poly(box);
  }
  const op = mode === 'pop' ? Math.min(1, reveal * 3) : 1;
  const ptsStr = pts.map((p) => p.join(',')).join(' ');
  const L = perim(pts);
  if (reveal <= 0 && border <= 0) return null;
  return (
    <div style={{position: 'absolute', inset: 0, opacity: op, ...style}}>
      <div style={{position: 'absolute', inset: 0, clipPath: clip}}>
        {shadow ? (
          <svg width={1080} height={1920} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
            <polygon points={pts.map((p) => `${p[0] + shadow},${p[1] + shadow}`).join(' ')} fill="rgba(0,0,0,0.75)" />
          </svg>
        ) : null}
        <div style={{position: 'absolute', inset: 0, clipPath: poly(pts), background: bg}}>
          {children}
          {dim > 0 ? <div style={{position: 'absolute', inset: 0, background: `rgba(8,7,10,${dim})`}} /> : null}
        </div>
      </div>
      <svg width={1080} height={1920} style={{position: 'absolute', inset: 0, overflow: 'visible', pointerEvents: 'none'}}>
        {highlight > 0 ? (
          <polygon points={ptsStr} fill="none" stroke={C.amber} strokeWidth={bw + 14} strokeLinejoin="round" opacity={highlight} style={{filter: `drop-shadow(0 0 ${18 * highlight}px ${C.amber})`}} />
        ) : null}
        <polygon points={ptsStr} fill="none" stroke={C.ink} strokeWidth={bw + 8} strokeLinejoin="round" strokeDasharray={L} strokeDashoffset={L * (1 - border)} />
        <polygon points={ptsStr} fill="none" stroke={borderColor} strokeWidth={bw} strokeLinejoin="round" strokeDasharray={L} strokeDashoffset={L * (1 - border)} />
      </svg>
    </div>
  );
};

/** Jagged torn-paper edge polygon points between two points (for tears & torn cards). */
export const tornLine = (a: Pt, b: Pt, segs = 26, amp = 18, seed = 1): Pt[] => {
  const out: Pt[] = [];
  const nx = -(b[1] - a[1]);
  const ny = b[0] - a[0];
  const nl = Math.hypot(nx, ny) || 1;
  for (let i = 0; i <= segs; i++) {
    const t = i / segs;
    const j = i === 0 || i === segs ? 0 : (rnd(i * 13 + seed) - 0.5) * 2 * amp;
    out.push([a[0] + (b[0] - a[0]) * t + (nx / nl) * j, a[1] + (b[1] - a[1]) * t + (ny / nl) * j]);
  }
  return out;
};
