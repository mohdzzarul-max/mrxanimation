import React from 'react';
import {AbsoluteFill, Img, interpolate, useCurrentFrame} from 'remotion';
import {MrX} from '../characters/MrX';
import {XBot} from '../characters/XBot';
import {Burst, Grain, Halftone, PaperBg, Rays} from '../components/Backgrounds';
import {BrushUnderline, KineticText} from '../components/KineticText';
import {Book3D, PriceTag} from '../components/Props';
import {SpeechBubble} from '../components/SpeechBubble';
import {PageFlip} from '../components/Transition';
import {A} from '../config/assets';
import {BRAND, C, FONT} from '../config/brand';
import {SCENES} from '../config/timeline';
import {autoBlink, clamp, E, noise1, ramp, shake, spr, talk} from '../lib/anim';

/**
 * SCENE 06 — FINAL SALES REVEAL (00:50–01:00), local 0-300.
 * 0-14 page lands / 18 RM800 tag struck through & dropped / 40 RM10.90 slam / 30 X-BOT line /
 * 100 CTA / 140 brand lock-up / 170 slogan. Everything holds from local ~175 (≥ 4 s) to the end.
 */
export const FinalCTA: React.FC = () => {
  const f = useCurrentFrame();
  const from = SCENES.cta.from;
  const flip = ramp(f, 0, 14, E.out);
  const tk = talk(f + from, 1530, 1660, 8);
  const oldIn = spr(f, 14, {damping: 10});
  const strike = ramp(f, 26, 34, E.out);
  const oldDrop = ramp(f, 36, 52, E.in);
  const price = f - 40;
  const pr = spr(f, 40, {damping: 8, stiffness: 240});
  const sh = shake(f, 41, 24, 10, 5);
  const cta = spr(f, 100, {damping: 10, stiffness: 160});
  const pulse = f > 120 ? 1 + Math.sin((f - 120) * 0.25) * 0.035 : 1;
  const brand = spr(f, 140, {damping: 14, stiffness: 120});
  const shine = interpolate((f - 150) % 90, [0, 30], [-0.3, 1.3], clamp);
  return (
    <AbsoluteFill style={{background: C.ink}}>
      <div style={{position: 'absolute', inset: 0, transform: `translate(${sh.x}px, ${sh.y}px)`}}>
        <PaperBg tone="dark" halftone={0.12} vignette={0.6} />
        <Rays cx={540} cy={640} rot={f * 0.3} opacity={0.16} count={28} />
        <AbsoluteFill style={{background: 'radial-gradient(circle at 540px 640px, rgba(255,184,28,0.45) 0%, rgba(0,0,0,0) 42%)'}} />
        <Halftone opacity={0.1} color={C.amber} />
        {/* book hero */}
        <Book3D x={540} y={650 + Math.sin(f * 0.06) * 10} w={370} ry={-16 + Math.sin(f * 0.04) * 5} rx={5} rz={-2} />
        {/* characters flank the product */}
        <XBot
          x={195}
          y={1015}
          height={400}
          expr={f < 40 ? 'surprised' : 'happy'}
          look={{x: 10, y: -6}}
          blink={autoBlink(f, 91, 70)}
          talk={tk}
          armR={{x: 1090, y: 380 + Math.sin(f * 0.15) * 10, hand: 'thumb', rot: -6}}
          armL={{x: 260, y: 640, hand: 'fist'}}
          hop={f >= 40 && f < 56 ? Math.sin(((f - 40) / 16) * Math.PI) * 120 : 0}
          capLift={f >= 50 && f < 70 ? Math.sin(((f - 50) / 20) * Math.PI) * 40 : 0}
          lean={4}
        />
        <MrX x={900 + noise1(f * 0.05, 6) * 4} y={1060} height={560} view="thumbChin" squash={1 + Math.sin(f * 0.1) * 0.006} />
        {/* old price callback */}
        {f >= 14 && oldDrop < 1 ? (
          <div style={{position: 'absolute', inset: 0, transform: `translateY(${oldDrop * 900}px) rotate(${oldDrop * 30}deg)`, transformOrigin: '300px 1100px', opacity: 1 - oldDrop}}>
            <PriceTag x={180} y={1020} text={BRAND.hookPrice} swing={-8} scale={0.7 * oldIn} strike={strike} />
          </div>
        ) : null}
        {/* new price */}
        {price >= 0 ? (
          <>
            <Burst cx={540} cy={1170} r={250 * Math.min(1, pr)} fill={C.red} spikes={24} rot={f * 0.4} sw={10} />
            <KineticText text={BRAND.price} f={price} mode="slam" x={540} y={1065} size={220} color={C.amber} strokeW={12} stroke={C.ink} shadow={`10px 10px 0 ${C.ink}`} rotate={-3} />
            <div style={{position: 'absolute', left: 880, top: 1000, transform: `rotate(12deg) scale(${spr(f, 50, {damping: 8})})`, background: C.offWhite, color: C.ink, border: `6px solid ${C.ink}`, fontFamily: FONT.display, fontSize: 52, padding: '0 14px', boxShadow: `6px 6px 0 ${C.ink}`}}>JE!</div>
          </>
        ) : null}
        {/* CTA */}
        {f >= 100 ? (
          <div style={{position: 'absolute', left: 90, top: 1318, width: 900, height: 120, transform: `scale(${cta * pulse})`, transformOrigin: '540px 1378px'}}>
            <div style={{position: 'absolute', inset: 0, background: C.amber, border: `8px solid ${C.ink}`, borderRadius: 70, boxShadow: `10px 10px 0 ${C.ink}`, overflow: 'hidden'}}>
              <div style={{position: 'absolute', top: 0, bottom: 0, width: 120, left: `${shine * 100}%`, background: 'rgba(255,255,255,0.55)', transform: 'skewX(-20deg)'}} />
            </div>
            <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 18, fontFamily: FONT.sans, fontWeight: 900, fontSize: 42, color: C.ink, letterSpacing: '0.01em', whiteSpace: 'nowrap'}}>
              <svg width={58} height={58} viewBox="0 0 58 58">
                <path d="M 6 10 H 52 V 40 H 24 L 12 52 V 40 H 6 Z" fill={C.ink} />
                <circle cx={18} cy={25} r={4} fill={C.amber} />
                <circle cx={29} cy={25} r={4} fill={C.amber} />
                <circle cx={40} cy={25} r={4} fill={C.amber} />
              </svg>
              {BRAND.cta}
            </div>
          </div>
        ) : null}
        {/* brand lock-up */}
        {f >= 140 ? (
          <div style={{position: 'absolute', left: 0, right: 0, top: 1475, textAlign: 'center', opacity: brand, transform: `translateY(${(1 - brand) * 40}px)`}}>
            <Img src={A.brand.wordmark} style={{width: 520}} />
            <div style={{fontFamily: FONT.sans, fontWeight: 800, fontSize: 24, letterSpacing: '0.5em', color: C.paper, marginTop: 4}}>{BRAND.series}</div>
          </div>
        ) : null}
        {/* slogan */}
        <KineticText text={BRAND.sloganA} f={f - 168} mode="slam" x={540} y={150} size={120} color={C.offWhite} rotate={-3} />
        <KineticText text={BRAND.sloganB} f={f - 178} mode="words" x={540} y={268} size={84} color={C.amber} stagger={3} rotate={-3} />
        {f >= 186 ? <BrushUnderline x={190} y={372} w={700} p={ramp(f, 186, 200)} color={C.red} thick={14} /> : null}
      </div>
      <SpeechBubble id="L7" sceneFrom={from} x={60} y={170} w={780} tail={[200, 590]} shout size={48} emphasis={['RM10.90', 'yakin']} />
      <PageFlip p={1 - flip}>
        <Halftone opacity={0.15} color="#000" />
      </PageFlip>
      <Grain opacity={0.12} />
    </AbsoluteFill>
  );
};
