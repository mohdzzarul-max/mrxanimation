import React from 'react';
import {interpolate} from 'remotion';
import {C, FONT} from '../config/brand';
import {clamp, E, rnd, spr} from '../lib/anim';

/**
 * Reusable kinetic typography. All modes are pure functions of `f` (frame relative to the text's start).
 *  - words: word-by-word pop with masked rise
 *  - chars: character stagger with rotation & overshoot
 *  - slam: whole phrase slams from large scale with impact squash
 *  - assemble: characters fly in from scattered fragments (text fragmentation) and can shatter out
 *  - wipe: masked left->right reveal with tracking animation
 */
export type KTMode = 'words' | 'chars' | 'slam' | 'assemble' | 'wipe';
export type KTProps = {
  text: string;
  f: number;
  mode?: KTMode;
  x: number;
  y: number;
  size?: number;
  color?: string;
  stroke?: string;
  strokeW?: number;
  font?: string;
  weight?: number;
  align?: 'left' | 'center' | 'right';
  width?: number;
  stagger?: number;
  shadow?: string | null;
  highlight?: Record<string, string>;
  out?: number; // frame (relative) at which to exit
  outMode?: 'shatter' | 'drop' | 'fade';
  rotate?: number;
  tracking?: number;
  lineHeight?: number;
  upper?: boolean;
  seed?: number;
  style?: React.CSSProperties;
};

export const KineticText: React.FC<KTProps> = ({
  text, f, mode = 'words', x, y, size = 96, color = C.offWhite, stroke = C.ink, strokeW = 0, font = FONT.display, weight = 400,
  align = 'center', width = 960, stagger = 3, shadow = `6px 6px 0 ${C.ink}`, highlight = {}, out, outMode = 'drop', rotate = 0,
  tracking = 0.02, lineHeight = 1.02, upper = false, seed = 1, style,
}) => {
  if (f < -2) return null;
  const txt = upper ? text.toUpperCase() : text;
  const outT = out !== undefined ? Math.max(0, f - out) : 0;
  const base: React.CSSProperties = {
    position: 'absolute', left: align === 'center' ? x - width / 2 : align === 'right' ? x - width : x, top: y, width,
    textAlign: align, fontFamily: font, fontWeight: weight, fontSize: size, lineHeight, color,
    letterSpacing: `${tracking}em`, transform: `rotate(${rotate}deg)`, transformOrigin: 'center',
    WebkitTextStroke: strokeW ? `${strokeW}px ${stroke}` : undefined, paintOrder: 'stroke fill',
    textShadow: shadow ?? undefined, ...style,
  };
  const exitStyle = (i: number): React.CSSProperties => {
    if (!outT) return {};
    const t = Math.max(0, outT - i * 0.6);
    if (outMode === 'fade') return {opacity: interpolate(t, [0, 8], [1, 0], clamp)};
    if (outMode === 'shatter') {
      const ang = (rnd(i + seed * 7) - 0.5) * 2;
      return {transform: `translate(${ang * t * 26}px, ${t * t * 1.4 - t * 10}px) rotate(${ang * t * 14}deg)`, opacity: interpolate(t, [4, 14], [1, 0], clamp)};
    }
    const p = interpolate(t, [0, 10], [0, 1], {...clamp, easing: E.in});
    return {transform: `translateY(${p * 140}px)`, opacity: 1 - p};
  };

  if (mode === 'slam') {
    const p = interpolate(f, [0, 7], [0, 1], {...clamp, easing: E.out});
    const sc = interpolate(p, [0, 1], [2.8, 1]);
    const squ = f >= 7 && f < 13 ? 1 + Math.sin(((f - 7) / 6) * Math.PI) * 0.08 : 1;
    return (
      <div style={{...base, opacity: Math.min(1, f / 3), transform: `rotate(${rotate}deg) scale(${sc * squ}, ${sc / squ})`, filter: f < 5 ? `blur(${(5 - f) * 1.5}px)` : undefined, ...exitStyle(0)}}>
        {txt}
      </div>
    );
  }
  if (mode === 'wipe') {
    const p = interpolate(f, [0, 14], [0, 1], {...clamp, easing: E.out});
    return (
      <div style={{...base, clipPath: `inset(-20% ${100 - p * 100}% -20% -5%)`, letterSpacing: `${tracking + (1 - p) * 0.25}em`, ...exitStyle(0)}}>
        {txt}
      </div>
    );
  }
  const words = txt.split(' ');
  let ci = 0;
  return (
    <div style={base}>
      {words.map((w, wi) => {
        const hl = highlight[w.replace(/[^A-Za-z0-9%≠]/g, '')] ?? highlight[w];
        if (mode === 'words') {
          const s = spr(f, wi * stagger, {damping: 11, stiffness: 180});
          const rise = interpolate(s, [0, 1], [0.9, 0]);
          return (
            <span key={wi} style={{display: 'inline-block', overflow: 'visible', marginRight: '0.22em', ...exitStyle(wi)}}>
              <span style={{display: 'inline-block', transform: `translateY(${rise * size}px) scale(${0.6 + 0.4 * s}) rotate(${(1 - s) * (rnd(wi + seed) - 0.5) * 30}deg)`, opacity: Math.min(1, s * 2.5), color: hl ?? color}}>
                {w}
              </span>
            </span>
          );
        }
        return (
          <span key={wi} style={{display: 'inline-block', marginRight: '0.22em', whiteSpace: 'nowrap'}}>
            {w.split('').map((ch, k) => {
              const i = ci++;
              const s = spr(f, i * (stagger / 2), {damping: 10, stiffness: 200});
              let tr = '';
              if (mode === 'assemble') {
                const dx = (rnd(i * 3 + seed) - 0.5) * 900;
                const dy = (rnd(i * 5 + seed) - 0.5) * 700;
                const r = (rnd(i * 11 + seed) - 0.5) * 220;
                tr = `translate(${dx * (1 - s)}px, ${dy * (1 - s)}px) rotate(${r * (1 - s)}deg) scale(${0.4 + 0.6 * s})`;
              } else {
                tr = `translateY(${(1 - s) * size * 0.8}px) rotate(${(1 - s) * (rnd(i + seed) - 0.5) * 50}deg) scale(${0.3 + 0.7 * s})`;
              }
              return (
                <span key={k} style={{display: 'inline-block', transform: tr, opacity: Math.min(1, s * 3), color: hl ?? color, ...exitStyle(i)}}>
                  {ch}
                </span>
              );
            })}
          </span>
        );
      })}
    </div>
  );
};

/** Animated brush underline that draws on. */
export const BrushUnderline: React.FC<{x: number; y: number; w: number; p: number; color?: string; thick?: number; seed?: number}> = ({x, y, w, p, color = C.amber, thick = 16, seed = 2}) => {
  const d = `M ${x} ${y} Q ${x + w * 0.4} ${y + 10 - rnd(seed) * 20} ${x + w} ${y - 6}`;
  return (
    <svg width={1080} height={1920} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
      <path d={d} stroke={color} strokeWidth={thick} fill="none" strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} />
    </svg>
  );
};
