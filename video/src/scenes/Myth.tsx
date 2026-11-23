import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {MrX} from '../characters/MrX';
import {XBot} from '../characters/XBot';
import {Grain, Halftone, PaperBg, SpeedLines} from '../components/Backgrounds';
import {ComicPanel, Pt} from '../components/ComicPanel';
import {KineticText} from '../components/KineticText';
import {PerfumeBottle, PriceTag} from '../components/Props';
import {SpeechBubble} from '../components/SpeechBubble';
import {BarWipe, Camera, InkIris} from '../components/Transition';
import {BRAND, C, FONT} from '../config/brand';
import {SCENES} from '../config/timeline';
import {autoBlink, clamp, E, kf, noise1, ramp, shake, spr, talk} from '../lib/anim';

/**
 * SCENE 02 — X-BOT DESTROYS THE MYTH (00:06–00:15), local frames 0-270.
 * 0-30 X-BOT jump-in (anticipation, land squash, cap follow-through) / 26 "Eh, belum tentu!" finger wag /
 * 58 split-screen comparison / 118 point gesture triggers "HARGA ≠ KETAHANAN" / 246 bar wipe out.
 */
const LEFT: Pt[] = [[40, 300], [560, 300], [510, 990], [40, 990]];
const RIGHT: Pt[] = [[580, 300], [1040, 300], [1040, 990], [530, 990]];

const Meter: React.FC<{x: number; y: number; f: number; seed: number; label: string}> = ({x, y, f, seed, label}) => {
  const a = -60 + 120 * (0.5 + noise1(f * 0.12, seed) * 0.5);
  return (
    <div style={{position: 'absolute', left: x - 150, top: y, width: 300, textAlign: 'center'}}>
      <svg width={300} height={160} viewBox="0 0 300 160">
        <path d="M 30 150 A 120 120 0 0 1 270 150" fill="none" stroke={C.smoke} strokeWidth={26} />
        <path d="M 30 150 A 120 120 0 0 1 270 150" fill="none" stroke="url(#mg)" strokeWidth={18} />
        <defs>
          <linearGradient id="mg">
            <stop offset="0" stopColor={C.red} />
            <stop offset="0.5" stopColor={C.amber} />
            <stop offset="1" stopColor="#7cd36b" />
          </linearGradient>
        </defs>
        <g transform={`rotate(${a} 150 150)`}>
          <path d="M 144 150 L 150 52 L 156 150 Z" fill={C.offWhite} stroke={C.ink} strokeWidth={4} />
        </g>
        <circle cx={150} cy={150} r={14} fill={C.ink} stroke={C.offWhite} strokeWidth={4} />
        <text x={150} y={118} textAnchor="middle" fontFamily="Bangers" fontSize={64} fill={C.offWhite} stroke={C.ink} strokeWidth={4} paintOrder="stroke">
          ?
        </text>
      </svg>
      <div style={{fontFamily: FONT.sans, fontWeight: 800, fontSize: 30, color: C.paper, letterSpacing: '0.12em'}}>{label}</div>
    </div>
  );
};

export const Myth: React.FC = () => {
  const f = useCurrentFrame();
  const from = SCENES.myth.from;
  // X-BOT entrance arc
  const jt = ramp(f, 2, 20, E.linear);
  const xbX = interpolate(jt, [0, 1], [1240, 790]);
  const hop = f < 20 ? Math.sin(jt * Math.PI) * 420 + (1 - jt) * 0 : 0;
  const landSq = f >= 20 ? 1 - Math.sin(Math.min(1, (f - 20) / 10) * Math.PI) * 0.2 * Math.exp(-(f - 20) / 14) : f < 4 ? 1 - (f / 4) * 0.12 : 1.08;
  const capLift = f >= 20 ? Math.max(0, Math.sin((f - 20) * 0.5) * 40 * Math.exp(-(f - 20) * 0.12)) : 18;
  const sh = shake(f, 20, 16, 10, 5);
  const wag = f >= 26 && f < 86 ? Math.sin(f * 0.9) * 22 : 0;
  const tX = talk(f + from, 206, 262, 3) + talk(f + from, 266, 420, 5);
  // point gesture -> infographic
  const pointT = ramp(f, 112, 120, E.back);
  const armR = f < 26
    ? {x: 1060, y: 620, hand: 'open' as const, rot: 10}
    : f < 100
      ? {x: 1050, y: 360, hand: 'pointUp' as const, rot: wag}
      : {x: interpolate(pointT, [0, 1], [1050, 930]), y: interpolate(pointT, [0, 1], [360, 260]), hand: 'pointUp' as const, rot: interpolate(pointT, [0, 1], [0, -38])};
  const armL = {x: 300, y: 700, hand: 'fist' as const, rot: 0};
  const split = spr(f, 56, {damping: 14, stiffness: 120});
  const split2 = spr(f, 64, {damping: 14, stiffness: 120});
  const neq = f - 120;
  const slash = ramp(f, 128, 138, E.out);
  const exitP = interpolate(f, [244, 270], [0, 1], clamp);
  const irisR = interpolate(f, [0, 14], [0, 2300], {...clamp, easing: E.out});
  return (
    <AbsoluteFill>
      <Camera x={sh.x} y={sh.y} zoom={kf(f, [[0, 1.06], [60, 1], [200, 1.03]], E.out)}>
        <PaperBg tone="dark" halftone={0.14} />
        <SpeedLines cx={790} cy={1300} opacity={interpolate(f, [16, 40], [0.35, 0], clamp)} color={C.amber} />
        {/* split-screen comparison */}
        <ComicPanel pts={LEFT} reveal={split} border={split} mode="wipeD" bg="#2a1a0a">
          <AbsoluteFill style={{background: `radial-gradient(circle at 30% 45%, #6b3f0c, #150d05 70%)`}} />
          <Halftone opacity={0.16} color={C.amber} />
          <PerfumeBottle variant="luxe" x={270} y={760} h={380} shine={ramp(f, 70, 100)} />
          <PriceTag x={290} y={420} text={BRAND.hookPrice} swing={-6 + Math.sin(f * 0.12) * 3} scale={0.5} />
          <Meter x={272} y={780} f={f} seed={3} label="KETAHANAN" />
        </ComicPanel>
        <ComicPanel pts={RIGHT} reveal={split2} border={split2} mode="wipeU" bg="#0f1a20">
          <AbsoluteFill style={{background: `radial-gradient(circle at 70% 45%, #20404d, #0a1115 70%)`}} />
          <Halftone opacity={0.16} color="#8fd3ff" />
          <PerfumeBottle variant="basic" x={790} y={760} h={360} shine={ramp(f, 80, 110)} />
          <PriceTag x={800} y={440} text={BRAND.cheapPrice} swing={8 + Math.sin(f * 0.1 + 1) * 3} scale={0.5} color={C.blue} />
          <Meter x={785} y={780} f={f} seed={9} label="KETAHANAN" />
        </ComicPanel>
        <KineticText text="MAHAL" f={f - 66} mode="chars" x={290} y={325} size={70} color={C.amber} width={460} />
        <KineticText text="MURAH" f={f - 74} mode="chars" x={800} y={325} size={70} color="#8fd3ff" width={460} />
        {/* HARGA ≠ KETAHANAN infographic, triggered by the point gesture */}
        {neq >= 0 ? (
          <div style={{position: 'absolute', left: 60, top: 520, width: 960, height: 230, transform: `rotate(-4deg) scale(${spr(f, 120, {damping: 9, stiffness: 220})})`}}>
            <div style={{position: 'absolute', inset: 0, background: C.ink, border: `8px solid ${C.amber}`, boxShadow: `14px 14px 0 rgba(0,0,0,0.8)`}} />
            <div style={{position: 'absolute', left: 30, top: 42, width: 330, textAlign: 'center', fontFamily: FONT.display, fontSize: 130, color: C.offWhite, lineHeight: 1}}>HARGA</div>
            <div style={{position: 'absolute', left: 520, top: 58, width: 420, textAlign: 'center', fontFamily: FONT.display, fontSize: 104, color: C.amber, lineHeight: 1}}>KETAHANAN</div>
            <svg width={160} height={200} style={{position: 'absolute', left: 365, top: 15}}>
              <rect x={20} y={70} width={120} height={22} fill={C.offWhite} />
              <rect x={20} y={112} width={120} height={22} fill={C.offWhite} />
              <path d="M 120 30 L 40 175" stroke={C.red} strokeWidth={22} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - slash} />
            </svg>
          </div>
        ) : null}
        {/* characters */}
        <MrX
          x={250 + noise1(f * 0.05, 1) * 6}
          y={1840}
          height={600}
          expr={f < 30 ? 'terkejut' : f < 140 ? 'biasa' : 'fikir'}
          headRot={f < 30 ? 6 : 8 + Math.sin(f * 0.07) * 2}
          headX={30}
          lean={f < 30 ? -4 : 0}
          armR={f > 150 ? 20 : 0}
          armL={f < 30 ? 30 : 0}
          blink={autoBlink(f, 11)}
          breathe={Math.sin(f * 0.1) * 0.5 + 0.5}
        />
        <XBot
          x={xbX}
          y={1700}
          height={560}
          hop={hop}
          squash={landSq}
          capLift={capLift}
          capTilt={f < 20 ? -10 : Math.sin(f * 0.2) * 3 * Math.exp(-(f - 20) / 30)}
          lean={f < 20 ? -12 : wag * 0.15}
          expr={f < 20 ? 'surprised' : f < 112 ? 'normal' : f < 160 ? 'angry' : 'squint'}
          look={{x: f > 112 ? -14 : -6, y: f > 112 ? -10 : 0}}
          blink={autoBlink(f, 21, 70)}
          talk={tX}
          armR={armR}
          armL={armL}
          footL={f < 20 ? {x: -20, y: -40, r: -10} : {x: 0, y: 0}}
          footR={f < 20 ? {x: 20, y: -30, r: 10} : {x: 0, y: 0}}
        />
        {/* landing dust */}
        {f >= 20 && f < 40 ? (
          <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
            {[-1, 1].map((d) =>
              [0, 1, 2].map((i) => {
                const t = (f - 20) / 20;
                return <circle key={`${d}${i}`} cx={790 + d * (180 + t * 160 + i * 40)} cy={1690 - i * 18 - t * 30} r={(26 - i * 6) * (1 - t)} fill={C.paper} opacity={0.7 * (1 - t)} />;
              }),
            )}
          </svg>
        ) : null}
      </Camera>
      <SpeechBubble id="L2" sceneFrom={from} x={560} y={1060} w={470} tail={[820, 1180]} shout size={56} emphasis={['belum', 'tentu']} />
      <SpeechBubble id="L3" sceneFrom={from} x={40} y={1030} w={780} tail={[800, 1200]} size={42} emphasis={['bukan', 'jaminan']} />
      {f < 14 ? <InkIris cx={960} cy={1300} r={irisR} color={C.amber} invert /> : null}
      <BarWipe p={exitP} />
      <Grain opacity={0.14} />
    </AbsoluteFill>
  );
};
