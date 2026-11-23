import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {C, FONT} from '../config/brand';
import {LINES} from '../config/script';
import {clamp, E, rnd, spr} from '../lib/anim';

/**
 * Comic speech bubble bound to a dialogue line (config/script.ts). Words are lettered in at a natural
 * Malay speaking pace (~2.8 words/s) so the bubble doubles as an on-screen subtitle.
 * Frames are absolute — place it at the top level of a scene that starts at frame `sceneFrom`.
 */
export const SpeechBubble: React.FC<{
  id: string;
  sceneFrom: number;
  x: number;
  y: number;
  w: number;
  tail: [number, number];
  shout?: boolean;
  size?: number;
  emphasis?: string[];
}> = ({id, sceneFrom, x, y, w, tail, shout = false, size = 44, emphasis = []}) => {
  const f = useCurrentFrame() + sceneFrom;
  const line = LINES.find((l) => l.id === id)!;
  if (f < line.from - 2 || f > line.to + 10) return null;
  const words = line.text.split(' ');
  const perWord = Math.min(10.5, ((line.to - line.from) * 0.78) / words.length);
  const pop = spr(f, line.from, {damping: 11, stiffness: 190});
  const outP = interpolate(f, [line.to, line.to + 8], [0, 1], {...clamp, easing: E.in});
  const sc = (0.3 + 0.7 * pop) * (1 - outP * 0.6);
  // greedy wrap estimate (Montserrat 800 avg glyph ≈ 0.6em)
  let lines = 1;
  let cur = 0;
  const maxW = w - 80;
  for (const wd of words) {
    const ww = (wd.length + 1) * size * 0.6;
    if (cur + ww > maxW && cur > 0) {
      lines++;
      cur = ww;
    } else cur += ww;
  }
  const h = lines * size * 1.22 + 64;
  const cx = x + w / 2;
  const cy = y + h / 2;
  const isX = line.speaker === 'XBOT';
  // bubble outline path (ellipse-ish rounded rect, jagged when shouting)
  let body: string;
  if (shout) {
    const n = 26;
    const pts = [];
    for (let i = 0; i < n * 2; i++) {
      const a = (i / (n * 2)) * Math.PI * 2;
      const rr = i % 2 ? 1.0 : 1.14 + rnd(i) * 0.06;
      pts.push(`${cx + Math.cos(a) * (w / 2) * rr},${cy + Math.sin(a) * (h / 2 + 18) * rr}`);
    }
    body = `M ${pts.join(' L ')} Z`;
  } else {
    const r = Math.min(70, h / 2);
    body = `M ${x + r} ${y} H ${x + w - r} Q ${x + w} ${y} ${x + w} ${y + r} V ${y + h - r} Q ${x + w} ${y + h} ${x + w - r} ${y + h} H ${x + r} Q ${x} ${y + h} ${x} ${y + h - r} V ${y + r} Q ${x} ${y} ${x + r} ${y} Z`;
  }
  // tail: wedge from the bubble edge nearest the target
  const bx = Math.max(x + 60, Math.min(x + w - 60, tail[0] < cx ? cx - w * 0.18 : cx + w * 0.18));
  const by = tail[1] > cy ? y + h - 4 : y + 4;
  const tailD = `M ${bx - 34} ${by} Q ${(bx + tail[0]) / 2} ${(by + tail[1]) / 2} ${tail[0]} ${tail[1]} Q ${(bx + tail[0]) / 2 + 30} ${(by + tail[1]) / 2} ${bx + 34} ${by} Z`;
  const wob = Math.sin(f * 0.35) * (shout ? 1.2 : 0.4);
  return (
    <div style={{position: 'absolute', inset: 0, transformOrigin: `${tail[0]}px ${tail[1]}px`, transform: `scale(${sc}) rotate(${wob}deg)`, opacity: 1 - outP}}>
      <svg width={1080} height={1920} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
        <g transform="translate(10 12)" fill={C.ink}>
          <path d={body} />
          <path d={tailD} />
        </g>
        <path d={tailD} fill={C.cream} stroke={C.ink} strokeWidth={7} strokeLinejoin="round" />
        <path d={body} fill={C.cream} stroke={C.ink} strokeWidth={7} strokeLinejoin="round" />
        <path d={tailD} fill={C.cream} transform={`translate(0 ${tail[1] > cy ? -9 : 9})`} />
      </svg>
      {/* speaker tag */}
      <div
        style={{
          position: 'absolute', left: x + (isX ? w - 190 : 26), top: y - 30, padding: '4px 18px', background: isX ? C.amber : C.ink,
          color: isX ? C.ink : C.offWhite, fontFamily: FONT.display, fontSize: 34, letterSpacing: '0.06em', border: `5px solid ${C.ink}`,
          transform: `rotate(${isX ? 3 : -3}deg)`, boxShadow: `4px 4px 0 ${C.ink}`,
        }}
      >
        {isX ? 'X-BOT' : 'MR X'}
      </div>
      <div
        style={{
          position: 'absolute', left: x + 34, top: y + 30, width: w - 68, fontFamily: FONT.sans, fontWeight: 800, fontSize: size,
          lineHeight: 1.18, color: C.ink, textAlign: 'center',
        }}
      >
        {words.map((wd, i) => {
          const t = f - line.from - 3 - i * perWord;
          const s = interpolate(t, [0, 5], [0, 1], {...clamp, easing: E.back});
          const emph = emphasis.some((e) => wd.toLowerCase().startsWith(e.toLowerCase()));
          return (
            <span key={i} style={{display: 'inline-block', marginRight: '0.24em', opacity: interpolate(t, [0, 2], [0.12, 1], clamp), transform: `translateY(${(1 - s) * 10}px)`, color: emph ? C.red : C.ink}}>
              {wd}
            </span>
          );
        })}
      </div>
    </div>
  );
};
