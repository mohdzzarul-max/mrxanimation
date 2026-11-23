import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {MrX} from '../characters/MrX';
import {XBot} from '../characters/XBot';
import {Burst, Grain, Halftone, PaperBg, SpeedLines} from '../components/Backgrounds';
import {ComicPanel, Pt, tornLine} from '../components/ComicPanel';
import {KineticText} from '../components/KineticText';
import {PerfumeBottle, PriceTag} from '../components/Props';
import {SpeechBubble} from '../components/SpeechBubble';
import {Camera, Flash, InkIris} from '../components/Transition';
import {BRAND, C} from '../config/brand';
import {SCENES} from '../config/timeline';
import {autoBlink, clamp, E, kf, noise1, ramp, shake, spr, talk} from '../lib/anim';

/**
 * SCENE 01 — THE INSANE HOOK (00:00–00:06)
 * f0-5 bottle drops / f5 SLAM impact frame / f10 RM800 tag swings / f28 the impact tears the panel /
 * f36 Mr X reaction panel / f44 dialogue / f98 headline / f108 record scratch + dramatic pause / f150 X-BOT peeks / f168 ink wipe.
 */
export const Hook: React.FC = () => {
  const f = useCurrentFrame();
  const from = SCENES.hook.from;
  // --- bottle drop & slam
  const drop = interpolate(f, [0, 5], [-560, 0], {...clamp, easing: E.in});
  const land = f >= 5 ? spr(f, 5, {damping: 7, stiffness: 260}) : 0;
  const bSquash = f >= 5 ? 1 - Math.sin(Math.min(1, (f - 5) / 8) * Math.PI) * 0.16 * (1 - Math.min(1, (f - 5) / 14)) : 1;
  const impact = f === 5 || f === 6;
  const sh1 = shake(f, 5, 42, 16, 3);
  const sh2 = shake(f, 28, 26, 12, 9);
  const sh3 = shake(f, 108, 14, 8, 21);
  // --- tear (panel split)
  const tear = ramp(f, 27, 36, E.out);
  const topShift = -tear * 110;
  const topRot = -tear * 2.5;
  const lineA: Pt = [-40, 1250];
  const lineB: Pt = [1120, 1140];
  const torn = tornLine(lineA, lineB, 30, 22, 4);
  const topPoly: Pt[] = [[-40, -40], [1120, -40], ...[...torn].reverse()];
  const botPoly: Pt[] = [...torn, [1120, 1960], [-40, 1960]];
  const gap = tear * 34;
  // --- record scratch freeze + dramatic pause
  const scratch = f >= 108 && f < 114;
  const pause = ramp(f, 112, 165, E.inOut);
  const sat = f >= 110 ? interpolate(f, [110, 116, 160, 168], [1, 0.25, 0.25, 1], clamp) : 1;
  // --- tag swing
  const swing = f >= 9 ? 38 * Math.cos((f - 9) * 0.42) * Math.exp(-(f - 9) * 0.09) - 8 : -60;
  const tagIn = spr(f, 9, {damping: 9, stiffness: 160});
  // --- Mr X reaction
  const mrxIn = spr(f, 33, {damping: 10, stiffness: 170});
  const punch = kf(f, [[40, 1], [46, 1.08], [104, 1.1], [112, 1.16], [168, 1.2]], E.out);
  const tk = talk(f, 44, 140, 1);
  const peek = ramp(f, 148, 162, E.back);
  const wipeR = interpolate(f, [166, 180], [0, 2300], {...clamp, easing: E.in});

  const bottleScene = (
    <>
      <PaperBg tone="dark" halftone={0.1} />
      <SpeedLines cx={540} cy={820} opacity={f >= 5 ? interpolate(f, [5, 26], [0.55, 0.12], clamp) : 0} color={C.paper} />
      {f >= 5 ? <Burst cx={540} cy={860} r={330 * spr(f, 5, {damping: 9})} fill={C.amber} rot={f * 0.6} spikes={20} /> : null}
      {f >= 5 ? <Burst cx={540} cy={860} r={210 * spr(f, 6, {damping: 9})} fill={C.red} rot={-f} spikes={14} sw={8} /> : null}
      {/* table edge */}
      <div style={{position: 'absolute', left: -20, right: -20, top: 1250, height: 700, background: 'linear-gradient(#26232a, #0c0b0e)', borderTop: `8px solid ${C.ink}`}} />
      <div style={{position: 'absolute', left: -20, right: -20, top: 1258, height: 6, background: 'rgba(255,255,255,0.12)'}} />
      <div style={{position: 'absolute', inset: 0, transformOrigin: '540px 1250px', transform: `translateY(${drop}px) scale(${1 / Math.sqrt(bSquash)}, ${bSquash})`}}>
        <PerfumeBottle variant="luxe" x={540} y={1262} h={640} shine={interpolate(f, [14, 40], [0, 1], clamp)} />
      </div>
      {f >= 9 ? <PriceTag x={610} y={760} text={BRAND.hookPrice} swing={swing} scale={0.5 + 0.55 * tagIn} /> : null}
      {/* falling motion streaks */}
      {f < 6 ? (
        <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
          {[-150, -90, -30, 30, 90, 150].map((dx, i) => (
            <rect key={i} x={540 + dx - 4} y={drop + 200 - 300 - (i % 3) * 80} width={8} height={420 + (i % 2) * 160} rx={4} fill={C.paper} opacity={0.35} />
          ))}
        </svg>
      ) : null}
      {/* spotlight cone */}
      <div style={{position: 'absolute', left: 140, top: -100, width: 800, height: 1500, background: 'linear-gradient(rgba(255,230,170,0.16), rgba(255,230,170,0))', clipPath: 'polygon(40% 0, 60% 0, 100% 100%, 0 100%)'}} />
      {/* onomatopoeia */}
      {f >= 5 ? (
        <div style={{position: 'absolute', left: 0, right: 0, top: 1330, textAlign: 'center', fontFamily: 'Bangers', fontSize: 260, color: C.red, WebkitTextStroke: `10px ${C.ink}`, paintOrder: 'stroke fill', textShadow: `12px 12px 0 ${C.ink}`, transform: `rotate(-6deg) scale(${spr(f, 5, {damping: 7, stiffness: 300}) * 1})`, letterSpacing: '0.04em'}}>
          DUSH!
        </div>
      ) : null}
      <Halftone opacity={0.08} />
    </>
  );

  return (
    <AbsoluteFill style={{background: C.ink, filter: impact ? 'grayscale(1) invert(1) contrast(1.8)' : `saturate(${sat})`}}>
      <Camera x={sh1.x + sh2.x + sh3.x + (scratch ? (f % 2 ? 18 : -18) : 0)} y={sh1.y + sh2.y + sh3.y} rot={sh1.r + sh2.r} zoom={1 + land * 0.02 + pause * 0.04}>
        {/* TOP panel: the bottle (whole frame before the tear) */}
        <ComicPanel pts={f < 27 ? [[-60, -60], [1140, -60], [1140, 1980], [-60, 1980]] : topPoly} bw={0} shadow={0} bg="transparent" style={{transform: `translateY(${topShift - gap}px) rotate(${topRot}deg)`, transformOrigin: '540px 900px'}}>
          <div style={{position: 'absolute', inset: 0, transform: `translateY(${-tear * 160}px) scale(${1 - tear * 0.25})`, transformOrigin: '540px 1262px'}}>{bottleScene}</div>
        </ComicPanel>
        {/* BOTTOM panel: Mr X reaction, revealed by the tear */}
        {f >= 27 ? (
          <ComicPanel pts={botPoly} bw={0} shadow={0} bg={C.red} style={{transform: `translateY(${gap}px)`}}>
            <AbsoluteFill style={{background: `radial-gradient(circle at 50% 70%, ${C.amber} 0%, ${C.red} 45%, ${C.redDeep} 100%)`}} />
            <SpeedLines cx={540} cy={1560} color={C.ink} opacity={0.35} inner={420} spin={f * 0.004} seed={4} />
            <Halftone opacity={0.18} color="#000" size={16} />
            <div style={{position: 'absolute', inset: 0, transformOrigin: '730px 1500px', transform: `scale(${punch}) translateY(${(1 - mrxIn) * 700}px)`}}>
              <MrX
                x={730 + noise1(f * 0.3, 2) * 4}
                y={2400}
                height={1000}
                expr={f < 40 ? 'normal' : f < 150 ? 'terkejut' : 'biasa'}
                headRot={-3 + tk * 2 + (f > 112 && f < 150 ? noise1(f * 0.8, 5) * 1.2 : 0)}
                headY={-tk * 14}
                headScale={f >= 40 && f < 44 ? 1.08 : 1}
                armL={f > 36 ? 55 : 0}
                armR={f > 36 ? 55 : 0}
                blink={f < 40 ? autoBlink(f, 3) : 0}
                squash={1 + tk * 0.01}
                shadow={false}
              />
            </div>
            {/* sweat drop during the dramatic pause */}
            {f > 114 ? (
              <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
                <path
                  d={`M 990 ${1290 + ramp(f, 116, 160, E.in) * 140} q -30 46 0 62 q 30 -16 0 -62 Z`}
                  fill="#8fd3ff"
                  stroke={C.ink}
                  strokeWidth={6}
                />
              </svg>
            ) : null}
            {/* X-BOT peeking in from the right */}
            <XBot x={1260 - peek * 230} y={1560} height={560} lean={-14 * peek} expr="squint" look={{x: -18, y: 0}} armR={{x: 960, y: 640, hand: 'open', rot: -20}} shadow={false} />
          </ComicPanel>
        ) : null}
        {/* torn paper edges */}
        {f >= 27 ? (
          <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
            <polyline points={torn.map((p) => `${p[0]},${p[1] + topShift - gap + 6}`).join(' ')} fill="none" stroke={C.paper} strokeWidth={14} transform={`rotate(${topRot} 540 900)`} />
            <polyline points={torn.map((p) => `${p[0]},${p[1] + gap - 4}`).join(' ')} fill="none" stroke={C.paper} strokeWidth={12} />
          </svg>
        ) : null}
        {/* typography */}
        <KineticText text="RM800?!" f={f - 6} mode="assemble" x={540} y={150} size={250} color={C.amber} strokeW={10} stroke={C.ink} shadow={`10px 10px 0 ${C.ink}`} rotate={-4} out={90} outMode="shatter" seed={8} />
        {f >= 92 ? (
          <div style={{position: 'absolute', left: 0, right: 0, top: 165, height: 300, transform: `rotate(-3deg) scaleY(${spr(f, 92, {damping: 14})})`, background: C.ink, borderTop: `8px solid ${C.amber}`, borderBottom: `8px solid ${C.amber}`}} />
        ) : null}
        <KineticText text="PERFUME MAHAL" f={f - 96} mode="words" x={540} y={180} size={128} color={C.offWhite} stagger={4} highlight={{MAHAL: C.amber}} rotate={-3} />
        <KineticText text="MESTI TAHAN LAMA?!" f={f - 104} mode="words" x={540} y={310} size={118} color={C.offWhite} stagger={4} highlight={{TAHAN: C.red, LAMA: C.red}} rotate={-3} />
      </Camera>
      <SpeechBubble id="L1" sceneFrom={from} x={30} y={1200} w={520} tail={[520, 1470]} size={40} emphasis={['lapan', 'ratus', 'gila']} />
      {/* impact frame: inverted flash */}
      <Flash on={f === 28} color={C.paper} opacity={0.7} />
      {scratch ? <AbsoluteFill style={{background: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.25) 0 6px, transparent 6px 14px)'}} /> : null}
      {f >= 166 ? <InkIris cx={960} cy={1300} r={wipeR} color={C.amber} /> : null}
      <Grain opacity={0.16 + pause * 0.1} />
    </AbsoluteFill>
  );
};
