import React from 'react';
import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {MrX, MrXExpr} from '../characters/MrX';
import {Arm, XBot} from '../characters/XBot';
import {Grain, PaperBg, SpeedLines} from '../components/Backgrounds';
import {tornLine} from '../components/ComicPanel';
import {Splatter, Stamp} from '../components/Props';
import {SpeechBubble} from '../components/SpeechBubble';
import {Camera} from '../components/Transition';
import {C, FONT} from '../config/brand';
import {SCENES} from '../config/timeline';
import {autoBlink, clamp, E, noise1, ramp, shake, spr, talk} from '../lib/anim';

/**
 * SCENE 04 — DON'T FALL FOR CLAIMS (00:27–00:40), local 0-390.
 * 0 board yanked down & swings / items at 40,78,116,154 (marker-circled, each with a gag icon) /
 * 190 board tucks up for X-BOT's line / 322 list collapses -> 338 "CHECK DULU!" stamp / 372 page folds away.
 */
const ITEMS = ['TAHAN 24 JAM?', 'BAU 100% SAMA?', 'BAHAN PREMIUM?', 'SESUAI UNTUK SIAPA?'];
const T0 = [40, 78, 116, 154];
const BW = 960;
const BH = 1010;

const Gag: React.FC<{i: number; t: number}> = ({i, t}) => {
  if (t < 0) return null;
  const pop = spr(t, 0, {damping: 9, stiffness: 220});
  let g: React.ReactNode = null;
  if (i === 0) {
    const spin = t < 30 ? t * t * 0.9 : 810 + (t - 30) * 0.5;
    const zz = ramp(t, 30, 40);
    g = (
      <svg width={150} height={150} viewBox="-75 -75 150 150" style={{overflow: 'visible'}}>
        <circle r={56} fill={C.offWhite} stroke={C.ink} strokeWidth={8} />
        <line x1={0} y1={0} x2={0} y2={-38} stroke={C.ink} strokeWidth={8} strokeLinecap="round" transform={`rotate(${spin})`} />
        <line x1={0} y1={0} x2={26} y2={0} stroke={C.red} strokeWidth={8} strokeLinecap="round" transform={`rotate(${spin / 12})`} />
        <text x={40} y={-50} fontFamily="Bangers" fontSize={46} fill={C.blue} opacity={zz} transform={`translate(${zz * 10} ${-zz * 14})`}>
          Zz
        </text>
      </svg>
    );
  } else if (i === 1) {
    const glitch = t > 22;
    g = (
      <div style={{fontFamily: FONT.display, fontSize: 82, color: glitch ? C.red : C.ink, transform: glitch && t < 30 ? `translateX(${(t % 2 ? 6 : -6)}px) skewX(${t % 2 ? 10 : -10}deg)` : undefined}}>
        {glitch ? '??%' : '100%'}
      </div>
    );
  } else if (i === 2) {
    const fizz = ramp(t, 24, 36);
    g = (
      <svg width={160} height={140} viewBox="-80 -70 160 140" style={{overflow: 'visible'}}>
        {[[-34, -10, 34], [24, -30, 24], [30, 26, 18]].map(([x, y, r], k) => (
          <g key={k} transform={`translate(${x} ${y + fizz * 20}) scale(${(1 - fizz) * (1 + Math.sin(t * 0.5 + k) * 0.1)})`}>
            <path d={`M 0 ${-r} Q 4 -4 ${r} 0 Q 4 4 0 ${r} Q -4 4 ${-r} 0 Q -4 -4 0 ${-r} Z`} fill={C.amber} stroke={C.ink} strokeWidth={5} />
          </g>
        ))}
        {fizz > 0 ? [0, 1, 2].map((k) => <circle key={k} cx={-30 + k * 30} cy={10 - fizz * 30} r={14 + fizz * 14} fill="#8a8590" opacity={(1 - fizz) * 0.9 + 0.2} />) : null}
      </svg>
    );
  } else {
    g = (
      <svg width={180} height={140} viewBox="-90 -70 180 140" style={{overflow: 'visible'}}>
        {[-55, 0, 55].map((x, k) => (
          <g key={k} transform={`translate(${x} ${Math.sin(t * 0.25 + k * 2) * 5})`}>
            <circle cy={-6} r={16} fill={C.ink} />
            <path d="M -22 40 Q -22 14 0 14 Q 22 14 22 40 Z" fill={C.ink} />
            <text y={-30} textAnchor="middle" fontFamily="Bangers" fontSize={34} fill={C.red}>
              ?
            </text>
          </g>
        ))}
      </svg>
    );
  }
  return <div style={{transform: `scale(${pop}) rotate(${(1 - pop) * 30}deg)`}}>{g}</div>;
};

export const Claims: React.FC = () => {
  const f = useCurrentFrame();
  const from = SCENES.claims.from;
  const drop = spr(f, 0, {damping: 9, stiffness: 120});
  const boardY = interpolate(drop, [0, 1], [-1300, 170]);
  const swing = f > 6 ? 5 * Math.cos((f - 6) * 0.35) * Math.exp(-(f - 6) * 0.08) : 0;
  const tuck = ramp(f, 186, 206, E.inOut);
  const collapse = ramp(f, 322, 338, E.in);
  const stampP = ramp(f, 336, 342, E.out);
  const sh = shake(f, 8, 18, 10, 2);
  const sh2 = shake(f, 339, 34, 14, 7);
  const fold = ramp(f, 372, 390, E.in);
  const tX = talk(f + from, 1010, 1170, 4);
  // expressions & gestures
  const mexpr: MrXExpr = f < 50 ? 'biasa' : f < 96 ? 'terkejut' : f < 330 ? 'fikir' : 'gembira';
  const activeItem = T0.reduce((a, t, i) => (f >= t ? i : a), -1);
  let armR: Arm = {x: 905, y: -60 + 200, hand: 'fist', flip: true, rot: 180};
  let armL: Arm = {x: 300, y: 700, hand: 'fist'};
  if (f > 12) armR = {x: 1000, y: 700, hand: 'fist', flip: true};
  if (f > 30 && f < 190) armL = {x: 170, y: 330 - activeItem * 30, hand: 'point', rot: -150 + activeItem * 12, flip: true};
  if (f >= 200 && f < 330) {
    const g = Math.sin(f * 0.25);
    armR = {x: 1060 + g * 20, y: 420 + g * 30, hand: 'open', rot: 15 + g * 15};
    armL = {x: 230, y: 520, hand: 'pointUp', rot: -20 + g * 10, flip: true};
  }
  if (f >= 336) {
    armR = {x: 1050, y: 380, hand: 'thumb', rot: -10};
    armL = {x: 300, y: 700, hand: 'fist'};
  }
  return (
    <AbsoluteFill style={{background: C.ink}}>
      <AbsoluteFill style={{perspective: 2200}}>
        <AbsoluteFill style={{transformOrigin: '50% 100%', transform: `rotateX(${fold * 88}deg)`, opacity: 1 - fold * 0.3}}>
          <Camera x={sh.x + sh2.x} y={sh.y + sh2.y} rot={sh2.r}>
            <PaperBg tone="dark" halftone={0.1} />
            {f >= 336 ? <SpeedLines cx={540} cy={600} color={C.red} opacity={interpolate(f, [336, 360], [0.5, 0.15], clamp)} /> : null}
            {/* the claims board */}
            <div style={{position: 'absolute', left: 60, top: boardY, width: BW, height: BH, transformOrigin: '540px 0px', transform: `translateY(${-tuck * 10}px) scale(${1 - tuck * 0.2}) rotate(${swing}deg)`}}>
              <div style={{position: 'absolute', inset: 0, transform: 'translate(16px,18px)', background: 'rgba(0,0,0,0.7)', clipPath: `polygon(${[[0, 0], [BW, 0], ...tornLine([BW, BH], [0, BH], 24, 16, 9)].map((p) => `${p[0]}px ${p[1]}px`).join(',')})`}} />
              <div style={{position: 'absolute', inset: 0, clipPath: `polygon(${[[0, 0], [BW, 0], ...tornLine([BW, BH], [0, BH], 24, 16, 9)].map((p) => `${p[0]}px ${p[1]}px`).join(',')})`}}>
                <Img src={staticFile('textures/paper_cream.jpg')} style={{position: 'absolute', width: BW, height: BH + 40, objectFit: 'cover'}} />
                <div style={{position: 'absolute', inset: 0, backgroundImage: 'repeating-linear-gradient(0deg, rgba(47,143,224,0.18) 0 3px, transparent 3px 66px)', backgroundPosition: '0 30px'}} />
                <div style={{position: 'absolute', left: 120, top: 0, bottom: 0, width: 4, background: 'rgba(212,58,44,0.4)'}} />
              </div>
              <div style={{position: 'absolute', left: -10, right: -10, top: -10, height: 130, background: C.ink, border: `6px solid ${C.ink}`, boxShadow: `0 8px 0 ${C.amber}`}} />
              <div style={{position: 'absolute', left: BW / 2 - 90, top: -46, width: 180, height: 70, borderRadius: 16, background: 'linear-gradient(#cfd3d6,#7c8287)', border: `6px solid ${C.ink}`}} />
              <div style={{position: 'absolute', left: 0, right: 0, top: 22, textAlign: 'center', fontFamily: FONT.display, fontSize: 86, color: C.amber, letterSpacing: '0.04em', lineHeight: 1}}>
                CLAIM SELLER
                <span style={{color: C.offWhite}}> ?!</span>
              </div>
              {ITEMS.map((it, i) => {
                const t = f - T0[i];
                if (t < 0) return null;
                const wipe = ramp(t, 0, 12, E.out);
                const circ = ramp(t, 12, 24, E.out);
                const q = ramp(t, 10, 16, E.back);
                const y = 170 + i * 205;
                const cx = (1 - collapse) * 0 + collapse * (BW / 2 - 400);
                const cy = collapse * (420 - y);
                return (
                  <div key={i} style={{position: 'absolute', left: 0, top: y, width: BW, height: 180, transform: `translate(${cx}px, ${cy}px) scale(${1 - collapse * 0.7})`, opacity: 1 - collapse}}>
                    <div style={{position: 'absolute', left: 30, top: 30, width: 96, height: 96, border: `8px solid ${C.ink}`, background: C.offWhite, transform: `rotate(${-3 + i * 2}deg)`}}>
                      <div style={{position: 'absolute', inset: 0, textAlign: 'center', fontFamily: FONT.display, fontSize: 92, lineHeight: '96px', color: C.red, transform: `scale(${q})`}}>?</div>
                    </div>
                    <div style={{position: 'absolute', left: 160, top: 40, fontFamily: FONT.display, fontSize: i === 3 ? 78 : 92, lineHeight: 1, color: C.ink, whiteSpace: 'nowrap', clipPath: `inset(-20% ${100 - wipe * 100}% -20% 0)`}}>{it}</div>
                    <svg width={BW} height={180} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
                      <ellipse cx={150 + (i === 3 ? 330 : 280)} cy={84} rx={i === 3 ? 340 : 290} ry={66} fill="none" stroke={C.red} strokeWidth={9} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - circ} transform={`rotate(-3 ${430} 84)`} opacity={0.85} />
                    </svg>
                    <div style={{position: 'absolute', left: i === 3 ? 820 : 740, top: 10, width: 180, height: 160, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                      <Gag i={i} t={t - 6} />
                    </div>
                  </div>
                );
              })}
              {f >= 336 ? <Splatter cx={BW / 2} cy={520} p={ramp(f, 338, 346)} n={22} r={420} /> : null}
              <Stamp x={BW / 2} y={520} text="CHECK DULU!" p={stampP} size={170} rot={-8} sub="SEBELUM PERCAYA" />
            </div>
            <MrX
              x={230 + noise1(f * 0.05, 9) * 5}
              y={1900}
              height={600}
              expr={mexpr}
              headRot={f >= 96 && f < 330 ? 8 + Math.sin(f * 0.08) * 3 : -4}
              headScale={f >= 50 && f < 54 ? 1.08 : f >= 330 && f < 334 ? 1.08 : 1}
              armL={f >= 336 ? 45 : f >= 50 && f < 96 ? 35 : 0}
              armR={f >= 336 ? 45 : f >= 50 && f < 96 ? 35 : 0}
              squash={f >= 336 && f < 346 ? 1.06 : 1}
              blink={autoBlink(f, 51)}
            />
            <XBot
              x={850 + noise1(f * 0.05, 4) * 6}
              y={1880}
              height={470}
              expr={f < 200 ? 'squint' : f < 336 ? 'normal' : 'happy'}
              look={{x: -18, y: -14}}
              talk={tX}
              blink={autoBlink(f, 61, 70)}
              armL={armL}
              armR={armR}
              lean={f >= 200 && f < 330 ? Math.sin(f * 0.25) * 3 : -2}
              hop={f >= 336 && f < 350 ? Math.sin(((f - 336) / 14) * Math.PI) * 80 : 0}
              capLift={f >= 336 && f < 356 ? Math.sin(((f - 336) / 20) * Math.PI) * 40 : 0}
              squash={f >= 348 && f < 356 ? 0.9 : 1}
            />
          </Camera>
          <SpeechBubble id="L5" sceneFrom={from} x={30} y={1010} w={1020} tail={[820, 1420]} size={40} emphasis={['asas', 'claim', 'seller']} />
        </AbsoluteFill>
      </AbsoluteFill>
      <Grain opacity={0.14} />
    </AbsoluteFill>
  );
};
