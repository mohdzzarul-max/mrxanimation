import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {MrX} from '../characters/MrX';
import {Arm, XBot} from '../characters/XBot';
import {Burst, Grain, Halftone, PaperBg} from '../components/Backgrounds';
import {ComicPanel, Pt} from '../components/ComicPanel';
import {KineticText} from '../components/KineticText';
import {SpeechBubble} from '../components/SpeechBubble';
import {BarWipe, Camera} from '../components/Transition';
import {C, FONT} from '../config/brand';
import {SCENES} from '../config/timeline';
import {autoBlink, clamp, E, kf, noise1, ramp, spr, talk} from '../lib/anim';

/**
 * SCENE 03 — THE REAL FACTORS (00:15–00:27), local 0-360.
 * Panel wall opens (10-50) -> each module highlighted in turn as X-BOT points and Mr X hops between columns
 * (P1 60, P2 120, P3 180, P4 240) -> all light up + "BANYAK FAKTOR" badge (296) -> pull-cord hand-off (330-360).
 */
const PANELS: Pt[][] = [
  [[44, 280], [528, 270], [522, 668], [48, 676]],
  [[552, 270], [1036, 280], [1032, 676], [546, 668]],
  [[48, 700], [522, 692], [528, 1080], [44, 1088]],
  [[546, 692], [1032, 700], [1036, 1088], [552, 1080]],
];
const CENTERS: [number, number][] = [[286, 470], [792, 470], [286, 888], [792, 888]];
const TITLES = ['FORMULA & KOMPOSISI', 'CIRI BAHAN', 'KIMIA KULIT', 'CUACA & CARA PAKAI'];
const SUBS = ['Kepekatan & campuran nota', 'Nota ringan vs nota berat', 'Kulit kering vs berminyak', 'Suhu, lembap, cara sembur'];
const ACTIVE = [60, 120, 180, 240];

const IconFormula: React.FC<{f: number}> = ({f}) => {
  const fills = [ramp(f, 4, 22), ramp(f, 14, 32), ramp(f, 24, 42)];
  const bands = [
    {y0: 0, y1: 70, c: '#ffe08a', label: 'TOP'},
    {y0: 70, y1: 140, c: C.amber, label: 'HEART'},
    {y0: 140, y1: 210, c: C.amberDeep, label: 'BASE'},
  ];
  return (
    <svg width={360} height={240} viewBox="-180 -15 360 240">
      <defs>
        <clipPath id="pyr">
          <path d="M 0 0 L 120 210 L -120 210 Z" />
        </clipPath>
      </defs>
      <g clipPath="url(#pyr)">
        <rect x={-130} y={0} width={260} height={210} fill={C.charcoal2} />
        {bands.map((b, i) => (
          <rect key={i} x={-130} y={b.y1 - (b.y1 - b.y0) * fills[i]} width={260} height={(b.y1 - b.y0) * fills[i]} fill={b.c} />
        ))}
        <path d="M -130 70 H 130 M -130 140 H 130" stroke={C.ink} strokeWidth={6} />
      </g>
      <path d="M 0 0 L 120 210 L -120 210 Z" fill="none" stroke={C.paper} strokeWidth={7} strokeLinejoin="round" />
      {bands.map((b, i) => (
        <text key={i} x={i === 0 ? 50 : 82 + i * 14} y={b.y0 + 46} fontFamily="Montserrat" fontWeight={800} fontSize={21} fill={C.paper} opacity={fills[i]}>
          {b.label}
        </text>
      ))}
      {[0, 1, 2].map((i) => {
        const t = ((f + i * 11) % 34) / 34;
        return <path key={i} d={`M ${-14 + i * 14} ${-10 + t * 60} q -9 14 0 19 q 9 -5 0 -19 Z`} fill={C.amber} opacity={1 - t} />;
      })}
    </svg>
  );
};

const IconMolecule: React.FC<{f: number}> = ({f}) => {
  const light = [0, 1, 2, 3].map((i) => {
    const t = ((f * 0.9 + i * 22) % 80) / 80;
    return {x: -120 + i * 46 + Math.sin(f * 0.1 + i) * 10, y: 90 - t * 110, o: 1 - t};
  });
  return (
    <svg width={360} height={240} viewBox="-180 -20 360 240">
      {light.map((m, i) => (
        <g key={i} transform={`translate(${m.x} ${m.y}) rotate(${f * 3 + i * 40})`} opacity={m.o}>
          <line x1={-14} y1={0} x2={14} y2={0} stroke={C.paper} strokeWidth={4} />
          <circle cx={-14} cy={0} r={13} fill="#ffe08a" stroke={C.ink} strokeWidth={3} />
          <circle cx={14} cy={0} r={10} fill="#ffe08a" stroke={C.ink} strokeWidth={3} />
        </g>
      ))}
      <g transform={`translate(70 140) rotate(${Math.sin(f * 0.05) * 8})`}>
        {[0, 60, 120, 180, 240, 300].map((a, i) => {
          const r = 34;
          const x = Math.cos((a * Math.PI) / 180) * r;
          const y = Math.sin((a * Math.PI) / 180) * r;
          const x2 = Math.cos(((a + 60) * Math.PI) / 180) * r;
          const y2 = Math.sin(((a + 60) * Math.PI) / 180) * r;
          return (
            <g key={i}>
              <line x1={x} y1={y} x2={x2} y2={y2} stroke={C.paper} strokeWidth={5} />
              <line x1={x} y1={y} x2={x * 1.8} y2={y * 1.8} stroke={C.paper} strokeWidth={4} />
              <circle cx={x * 1.8} cy={y * 1.8} r={11} fill="#8a5a2b" stroke={C.ink} strokeWidth={3} />
              <circle cx={x} cy={y} r={14} fill={C.amberDeep} stroke={C.ink} strokeWidth={3} />
            </g>
          );
        })}
      </g>
      <text x={-60} y={8} fontFamily="Montserrat" fontWeight={800} fontSize={22} fill="#ffe08a">RINGAN: cepat naik</text>
      <text x={-170} y={150} fontFamily="Montserrat" fontWeight={800} fontSize={22} fill={C.amberDeep}>BERAT:</text><text x={-170} y={176} fontFamily="Montserrat" fontWeight={800} fontSize={22} fill={C.amberDeep}>lebih lekat</text>
    </svg>
  );
};

const IconSkin: React.FC<{f: number}> = ({f}) => {
  const wave = (y: number, a: number, ph: number) => {
    let d = `M -180 ${y}`;
    for (let x = -180; x <= 180; x += 20) d += ` L ${x} ${y + Math.sin(x * 0.05 + ph) * a}`;
    return d + ' L 180 230 L -180 230 Z';
  };
  return (
    <svg width={360} height={240} viewBox="-180 -20 360 240">
      <path d={wave(110, 8, f * 0.05)} fill="#f2b38d" stroke={C.ink} strokeWidth={5} />
      <path d={wave(150, 6, f * 0.05 + 1)} fill="#e08e6c" stroke={C.ink} strokeWidth={4} />
      <path d={wave(190, 5, f * 0.05 + 2)} fill="#c66b52" stroke={C.ink} strokeWidth={4} />
      <line x1={0} y1={-10} x2={0} y2={100} stroke={C.paper} strokeWidth={3} strokeDasharray="8 8" />
      {[0, 1, 2].map((i) => {
        const t = ((f + i * 14) % 42) / 42;
        return <path key={i} d={`M ${-120 + i * 36} ${90 - t * 90} q -10 16 0 22 q 10 -6 0 -22 Z`} fill="#8fd3ff" opacity={1 - t} stroke={C.ink} strokeWidth={2} />;
      })}
      {[0, 1, 2].map((i) => (
        <path key={i} d={`M ${50 + i * 40} 88 q -12 20 0 26 q 12 -6 0 -26 Z`} fill="#8fd3ff" stroke={C.ink} strokeWidth={3} transform={`translate(0 ${Math.sin(f * 0.12 + i) * 3})`} />
      ))}
      <text x={-150} y={40} fontFamily="Montserrat" fontWeight={800} fontSize={22} fill={C.paper}>KERING</text>
      <text x={30} y={40} fontFamily="Montserrat" fontWeight={800} fontSize={22} fill={C.paper}>BERMINYAK</text>
    </svg>
  );
};

const IconWeather: React.FC<{f: number}> = ({f}) => {
  const temp = 0.35 + 0.55 * (0.5 + 0.5 * Math.sin(f * 0.06));
  return (
    <svg width={360} height={240} viewBox="-180 -20 360 240">
      <g transform={`translate(-110 50) rotate(${f * 1.5})`}>
        {Array.from({length: 10}).map((_, i) => (
          <rect key={i} x={-5} y={-62} width={10} height={20} rx={4} fill={C.amber} transform={`rotate(${i * 36})`} />
        ))}
        <circle r={34} fill={C.amber} stroke={C.ink} strokeWidth={5} />
      </g>
      <g transform="translate(-20 0)">
        <rect x={-14} y={0} width={28} height={150} rx={14} fill={C.paper} stroke={C.ink} strokeWidth={5} />
        <rect x={-6} y={8 + 132 * (1 - temp)} width={12} height={132 * temp} fill={C.red} />
        <circle cx={0} cy={165} r={24} fill={C.red} stroke={C.ink} strokeWidth={5} />
      </g>
      <g transform="translate(60 70)">
        <rect x={0} y={20} width={50} height={80} rx={10} fill="#d9e6ea" stroke={C.ink} strokeWidth={5} />
        <rect x={12} y={0} width={26} height={22} rx={4} fill="#9aa1a6" stroke={C.ink} strokeWidth={4} />
        {[0, 1, 2, 3, 4].map((i) => {
          const t = ((f * 1.2 + i * 9) % 45) / 45;
          return <circle key={i} cx={44 + t * 80} cy={6 - t * 30 + Math.sin(i * 2 + f * 0.2) * 8} r={6 + t * 12} fill={C.paper} opacity={0.6 * (1 - t)} />;
        })}
      </g>
      <text x={-170} y={210} fontFamily="Montserrat" fontWeight={800} fontSize={20} fill={C.paper}>PANAS · LEMBAP · SEMBUR</text>
    </svg>
  );
};
const ICONS = [IconFormula, IconMolecule, IconSkin, IconWeather];

export const Factors: React.FC = () => {
  const f = useCurrentFrame();
  const from = SCENES.factors.from;
  const active = f >= 296 ? 4 : ACTIVE.reduce((a, s, i) => (f >= s ? i : a), -1);
  // Mr X hops between columns
  const hopKeys: [number, number, number][] = [[118, 230, 470], [178, 470, 230], [238, 230, 470]];
  let mx = 230;
  let my = 0;
  let moving = 0;
  let dir = 1;
  for (const [t0, a, b] of hopKeys) {
    if (f >= t0) {
      const p = ramp(f, t0, t0 + 16, E.inOut);
      mx = a + (b - a) * p;
      if (p > 0 && p < 1) {
        my = -Math.sin(p * Math.PI) * 90;
        moving = 1;
        dir = b > a ? 1 : -1;
      }
    }
  }
  const tk = talk(f + from, 560, 790, 2);
  // X-BOT pointing per active panel
  const pointArm = (i: number): {armL: Arm; armR: Arm} => {
    const restL: Arm = {x: 300, y: 700, hand: 'fist'};
    const restR: Arm = {x: 1000, y: 700, hand: 'fist', flip: true};
    if (i === 0) return {armL: {x: 170, y: 380, hand: 'point', rot: -150, flip: true}, armR: restR};
    if (i === 2) return {armL: {x: 150, y: 520, hand: 'point', rot: -175, flip: true}, armR: restR};
    if (i === 1) return {armL: restL, armR: {x: 1030, y: 250, hand: 'pointUp', rot: -8}};
    if (i === 3) return {armL: restL, armR: {x: 990, y: 300, hand: 'pointUp', rot: -38}};
    return {armL: {x: 230, y: 320, hand: 'open', rot: -20, flip: true}, armR: {x: 1080, y: 320, hand: 'open', rot: 20}};
  };
  const arms = active >= 0 ? pointArm(active) : {armL: {x: 300, y: 700, hand: 'fist' as const}, armR: {x: 1000, y: 700, hand: 'fist' as const, flip: true}};
  // pull cord hand-off
  const cord = ramp(f, 326, 338, E.back);
  const yank = ramp(f, 348, 356, E.in);
  const grab = f >= 342;
  const armRFinal: Arm = grab ? {x: 905, y: -60 + yank * 200, hand: 'fist', flip: true, rot: 180} : arms.armR;
  const enter = interpolate(f, [0, 20], [1, 2], clamp);
  const badge = spr(f, 296, {damping: 9, stiffness: 200});
  return (
    <AbsoluteFill>
      <Camera zoom={kf(f, [[0, 1.04], [60, 1], [296, 1], [306, 1.04], [330, 1.02]], E.out)} fy={700}>
        <PaperBg tone="dark" halftone={0.1} />
        <KineticText text="APA YANG BUAT PERFUME TAHAN LAMA?" f={f - 8} mode="words" x={540} y={150} size={66} color={C.offWhite} stagger={3} highlight={{TAHAN: C.amber, LAMA: C.amber}} width={1000} />
        {PANELS.map((pts, i) => {
          const rv = spr(f, 14 + i * 7, {damping: 13, stiffness: 150});
          const Icon = ICONS[i];
          const on = active === i || active === 4;
          const hl = on ? ramp(f, active === 4 ? 296 : ACTIVE[i], (active === 4 ? 296 : ACTIVE[i]) + 6) : 0;
          const [cx, cy] = CENTERS[i];
          const pop = on && active !== 4 ? Math.sin(ramp(f, ACTIVE[i], ACTIVE[i] + 10) * Math.PI) * 0.04 : 0;
          return (
            <div key={i} style={{position: 'absolute', inset: 0, transformOrigin: `${cx}px ${cy}px`, transform: `scale(${1 + pop})`}}>
              <ComicPanel pts={pts} reveal={rv} border={rv} mode="iris" bg={C.charcoal2} highlight={hl} dim={active >= 0 && !on ? 0.5 : 0}>
                <AbsoluteFill style={{background: `radial-gradient(circle at ${cx}px ${cy - 40}px, ${on ? '#3a2a12' : '#2a2830'}, ${C.charcoal} 70%)`}} />
                <Halftone opacity={0.1} color={on ? C.amber : '#fff'} />
                <div style={{position: 'absolute', left: cx - 180, top: cy - 160}}>
                  <Icon f={Math.max(0, f - 20 - i * 7)} />
                </div>
                <div style={{position: 'absolute', left: pts[0][0] + 22, top: pts[0][1] + 18, width: 64, height: 64, borderRadius: 32, background: on ? C.amber : C.paper, color: C.ink, fontFamily: FONT.display, fontSize: 44, textAlign: 'center', lineHeight: '68px', border: `5px solid ${C.ink}`}}>
                  {i + 1}
                </div>
                <div style={{position: 'absolute', left: cx - 230, width: 460, top: cy + 92, textAlign: 'center', fontFamily: FONT.display, fontSize: 52, color: on ? C.amber : C.offWhite, textShadow: `4px 4px 0 ${C.ink}`, lineHeight: 1}}>
                  {TITLES[i]}
                </div>
                <div style={{position: 'absolute', left: cx - 230, width: 460, top: cy + 148, textAlign: 'center', fontFamily: FONT.sans, fontWeight: 700, fontSize: 26, color: C.paper}}>{SUBS[i]}</div>
              </ComicPanel>
            </div>
          );
        })}
        {f >= 296 ? (
          <div style={{position: 'absolute', inset: 0, transformOrigin: '540px 684px', transform: `scale(${badge}) rotate(${(1 - badge) * -20 - 4}deg)`}}>
            <Burst cx={540} cy={684} r={270} fill={C.amber} spikes={22} rot={f * 0.5} />
            <div style={{position: 'absolute', left: 300, width: 480, top: 618, textAlign: 'center', fontFamily: FONT.display, fontSize: 56, lineHeight: 0.95, color: C.ink}}>
              BANYAK FAKTOR,
              <br />
              <span style={{color: C.red}}>BUKAN HARGA SAJA!</span>
            </div>
          </div>
        ) : null}
        {/* pull cord */}
        {f >= 326 ? (
          <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
            <line x1={960} y1={-20} x2={960} y2={-200 + cord * 1520 + yank * 120} stroke={C.paper} strokeWidth={8} />
            <circle cx={960} cy={-200 + cord * 1520 + yank * 120 + 30} r={30} fill="none" stroke={C.amber} strokeWidth={12} />
          </svg>
        ) : null}
        <MrX
          x={mx}
          y={1900 + my}
          height={600}
          view={moving ? '34' : 'front'}
          flip={moving ? dir < 0 : false}
          expr={f < 296 ? 'normal' : 'gembira'}
          headRot={-4 + tk * 3 + (active === 1 || active === 3 ? 6 : -6)}
          headY={-tk * 16}
          armR={active === 4 ? 40 : tk * 10}
          armL={active === 4 ? 40 : 0}
          squash={moving ? 1.06 : 1 + Math.sin(f * 0.1) * 0.01}
          blink={autoBlink(f, 31)}
        />
        <XBot
          x={860 + noise1(f * 0.04, 3) * 8}
          y={1860}
          height={470}
          expr={f >= 296 ? 'happy' : 'normal'}
          look={{x: active === 0 || active === 2 ? -20 : 6, y: active < 2 ? -18 : 0}}
          blink={autoBlink(f, 41, 70)}
          armL={arms.armL}
          armR={armRFinal}
          lean={active === 0 || active === 2 ? -6 : 3}
          squash={grab ? 1 + yank * -0.12 + (1 - yank) * 0.08 : 1}
          capLift={grab ? 20 * (1 - yank) : 0}
          hop={grab && yank < 1 ? 60 * (1 - yank) : 0}
        />
      </Camera>
      <SpeechBubble id="L4" sceneFrom={from} x={30} y={1110} w={1020} tail={[mx + 40, 1330 + my]} size={40} emphasis={['formula', 'bahan', 'kulit', 'keadaan', 'sekeliling']} />
      <BarWipe p={enter} />
      <Grain opacity={0.14} />
    </AbsoluteFill>
  );
};
