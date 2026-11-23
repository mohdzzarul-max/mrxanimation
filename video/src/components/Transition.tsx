import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C} from '../config/brand';
import {noise1} from '../lib/anim';

/** Camera: zoom/pan/rotate/shake around a focus point. Wrap scene content with it. */
export const Camera: React.FC<{zoom?: number; x?: number; y?: number; rot?: number; fx?: number; fy?: number; children: React.ReactNode; style?: React.CSSProperties}> = ({
  zoom = 1, x = 0, y = 0, rot = 0, fx = 540, fy = 960, children, style,
}) => (
  <AbsoluteFill style={{transformOrigin: `${fx}px ${fy}px`, transform: `translate(${x}px, ${y}px) rotate(${rot}deg) scale(${zoom})`, ...style}}>{children}</AbsoluteFill>
);

/** Diagonal ink bars that cover (p 0->1) then uncover (p 1->2). */
export const BarWipe: React.FC<{p: number; color?: string; bars?: number; angle?: number}> = ({p, color = C.ink, bars = 6, angle = -20}) => {
  if (p <= 0 || p >= 2) return null;
  const els = [];
  for (let i = 0; i < bars; i++) {
    const d = i * 0.08;
    const cover = Math.max(0, Math.min(1, (p - d) / (1 - (bars - 1) * 0.08)));
    const un = Math.max(0, Math.min(1, (p - 1 - d) / (1 - (bars - 1) * 0.08)));
    const left = un * 100;
    const width = Math.max(0, cover * 100 - un * 100);
    els.push(
      <div key={i} style={{position: 'absolute', top: `${(i / bars) * 100}%`, height: `${100 / bars + 0.6}%`, left: `${left}%`, width: `${width}%`, background: i % 2 ? color : C.charcoal2, borderTop: `6px solid ${C.amber}`}} />,
    );
  }
  return (
    <AbsoluteFill style={{transform: `rotate(${angle}deg) scale(1.9)`, transformOrigin: 'center'}}>
      {els}
    </AbsoluteFill>
  );
};

/** Organic ink blob iris wipe. r = radius in px. */
export const InkIris: React.FC<{cx: number; cy: number; r: number; color?: string; invert?: boolean; seed?: number}> = ({cx, cy, r, color = C.amber, invert = false, seed = 2}) => {
  const n = 48;
  const pts = [];
  for (let i = 0; i < n; i++) {
    const a = (i / n) * Math.PI * 2;
    const rr = r * (1 + noise1(i * 0.6, seed) * 0.08 + noise1(i * 2.1, seed + 3) * 0.04);
    pts.push(`${cx + Math.cos(a) * rr},${cy + Math.sin(a) * rr}`);
  }
  const blob = `M ${pts.join(' L ')} Z`;
  return (
    <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
      {invert ? <path d={`M -10 -10 H 1090 V 1930 H -10 Z ${blob}`} fillRule="evenodd" fill={color} /> : <path d={blob} fill={color} />}
    </svg>
  );
};

/** One-frame impact flash. kind: white flash or inverted "impact frame". */
export const Flash: React.FC<{on: boolean; color?: string; opacity?: number}> = ({on, color = '#fff', opacity = 1}) =>
  on ? <AbsoluteFill style={{background: color, opacity, mixBlendMode: 'normal'}} /> : null;

/** Page flip: a paper sheet sweeping across, hinged on the left edge. p 0..1 */
export const PageFlip: React.FC<{p: number; children?: React.ReactNode}> = ({p, children}) => {
  if (p <= 0 || p >= 1) return null;
  const ang = -180 * p;
  return (
    <AbsoluteFill style={{perspective: 2600}}>
      <AbsoluteFill style={{transformOrigin: '0% 50%', transform: `rotateY(${ang}deg)`, background: C.cream, boxShadow: `0 0 80px rgba(0,0,0,${0.6 * Math.sin(p * Math.PI)})`}}>
        <AbsoluteFill style={{background: `linear-gradient(90deg, rgba(0,0,0,${0.35 * p}) 0%, rgba(0,0,0,0) 40%)`}} />
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
