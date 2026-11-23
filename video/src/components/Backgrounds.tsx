import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {C} from '../config/brand';
import {rnd} from '../lib/anim';

export const PaperBg: React.FC<{tone?: 'dark' | 'cream'; tint?: string; halftone?: number; vignette?: number; style?: React.CSSProperties}> = ({
  tone = 'dark', tint, halftone = 0.12, vignette = 0.55, style,
}) => (
  <AbsoluteFill style={style}>
    <Img src={staticFile(`textures/paper_${tone}.jpg`)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
    {tint ? <AbsoluteFill style={{background: tint, mixBlendMode: 'multiply'}} /> : null}
    <Halftone opacity={halftone} color={tone === 'dark' ? '#ffffff' : '#000000'} />
    <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 45%, rgba(0,0,0,${vignette}) 100%)`}} />
  </AbsoluteFill>
);

/** CSS halftone dot screen (print feel). */
export const Halftone: React.FC<{opacity?: number; color?: string; size?: number; angle?: number; style?: React.CSSProperties}> = ({
  opacity = 0.12, color = '#fff', size = 14, angle = 25, style,
}) => (
  <AbsoluteFill
    style={{
      opacity,
      backgroundImage: `radial-gradient(${color} 22%, transparent 24%)`,
      backgroundSize: `${size}px ${size}px`,
      transform: `rotate(${angle}deg) scale(1.6)`,
      maskImage: 'radial-gradient(ellipse at 30% 20%, black 0%, transparent 70%)',
      WebkitMaskImage: 'radial-gradient(ellipse at 30% 20%, black 0%, transparent 70%)',
      ...style,
    }}
  />
);

/** Film/print grain that jitters every 2 frames (deterministic). */
export const Grain: React.FC<{opacity?: number}> = ({opacity = 0.18}) => {
  const f = useCurrentFrame();
  const k = Math.floor(f / 2);
  return (
    <AbsoluteFill style={{pointerEvents: 'none', overflow: 'hidden'}}>
      <Img
        src={staticFile('textures/grain.png')}
        style={{position: 'absolute', width: 1300, height: 2300, left: -rnd(k) * 200, top: -rnd(k + 9) * 360, opacity, mixBlendMode: 'overlay'}}
      />
    </AbsoluteFill>
  );
};

/** Comic speed / focus lines radiating from (cx, cy). */
export const SpeedLines: React.FC<{cx: number; cy: number; count?: number; color?: string; opacity?: number; inner?: number; seed?: number; spin?: number}> = ({
  cx, cy, count = 70, color = '#fff', opacity = 0.6, inner = 260, seed = 1, spin = 0,
}) => {
  const lines = [];
  for (let i = 0; i < count; i++) {
    const a = (i / count) * Math.PI * 2 + rnd(i + seed) * 0.05 + spin;
    const w = 0.006 + rnd(i * 3 + seed) * 0.018;
    const r0 = inner + rnd(i * 7 + seed) * 220;
    const r1 = 2600;
    const p = [
      [cx + Math.cos(a - w) * r1, cy + Math.sin(a - w) * r1],
      [cx + Math.cos(a) * r0, cy + Math.sin(a) * r0],
      [cx + Math.cos(a + w) * r1, cy + Math.sin(a + w) * r1],
    ];
    lines.push(<polygon key={i} points={p.map((q) => q.join(',')).join(' ')} fill={color} />);
  }
  return (
    <svg width={1080} height={1920} style={{position: 'absolute', inset: 0, opacity}}>
      {lines}
    </svg>
  );
};

/** Spiky impact burst. */
export const Burst: React.FC<{cx: number; cy: number; r: number; spikes?: number; fill?: string; stroke?: string; sw?: number; rot?: number; jag?: number; seed?: number; style?: React.CSSProperties}> = ({
  cx, cy, r, spikes = 18, fill = C.amber, stroke = C.ink, sw = 10, rot = 0, jag = 0.38, seed = 3, style,
}) => {
  const pts: string[] = [];
  for (let i = 0; i < spikes * 2; i++) {
    const a = (i / (spikes * 2)) * Math.PI * 2 + (rot * Math.PI) / 180;
    const rr = i % 2 === 0 ? r * (0.92 + rnd(i + seed) * 0.16) : r * (1 - jag) * (0.9 + rnd(i * 5 + seed) * 0.2);
    pts.push(`${cx + Math.cos(a) * rr},${cy + Math.sin(a) * rr}`);
  }
  return (
    <svg width={1080} height={1920} style={{position: 'absolute', inset: 0, overflow: 'visible', ...style}}>
      <polygon points={pts.join(' ')} fill={fill} stroke={stroke} strokeWidth={sw} strokeLinejoin="round" />
    </svg>
  );
};

/** Rotating sun-ray background. */
export const Rays: React.FC<{cx: number; cy: number; color?: string; count?: number; rot?: number; opacity?: number}> = ({
  cx, cy, color = C.amber, count = 24, rot = 0, opacity = 0.18,
}) => {
  const els = [];
  for (let i = 0; i < count; i++) {
    const a0 = ((i / count) * 360 + rot) * (Math.PI / 180);
    const a1 = a0 + (Math.PI / count) * 0.9;
    els.push(
      <polygon key={i} points={`${cx},${cy} ${cx + Math.cos(a0) * 2400},${cy + Math.sin(a0) * 2400} ${cx + Math.cos(a1) * 2400},${cy + Math.sin(a1) * 2400}`} fill={color} />,
    );
  }
  return (
    <svg width={1080} height={1920} style={{position: 'absolute', inset: 0, opacity}}>
      {els}
    </svg>
  );
};
