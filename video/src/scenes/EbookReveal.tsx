import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {MrX} from '../characters/MrX';
import {Arm, XBot} from '../characters/XBot';
import {Grain, Halftone, PaperBg, Rays} from '../components/Backgrounds';
import {KineticText} from '../components/KineticText';
import {Book3D} from '../components/Props';
import {SpeechBubble} from '../components/SpeechBubble';
import {PageFlip} from '../components/Transition';
import {BRAND, C, FONT} from '../config/brand';
import {SCENES} from '../config/timeline';
import {autoBlink, clamp, E, noise1, ramp, spr, talk} from '../lib/anim';

/**
 * SCENE 05 — THE E-BOOK REVEAL (00:40–00:50), local 0-300.
 * 0-12 a comic panel swings edge-on / 12-34 it unfolds as the e-book (3D) / 36 Mr X presents + line L6 /
 * 140 book slides left, benefits stack in (X-BOT gestures each) / 280 page flip to the end card.
 */
export const EbookReveal: React.FC = () => {
  const f = useCurrentFrame();
  const from = SCENES.ebook.from;
  const panelTurn = interpolate(f, [0, 12], [0, 90], {...clamp, easing: E.in});
  const bookIn = spr(f, 12, {damping: 12, stiffness: 110});
  const ry = interpolate(bookIn, [0, 1], [-90, -18]) + Math.sin(f * 0.05) * 4;
  const slide = ramp(f, 136, 156, E.inOut);
  const bx = interpolate(slide, [0, 1], [540, 300]);
  const by = interpolate(slide, [0, 1], [720, 690]) + Math.sin(f * 0.07) * 8;
  const bw = interpolate(slide, [0, 1], [420, 360]);
  const tk = talk(f + from, 1236, 1400, 6);
  const flip = ramp(f, 280, 300, E.inOut);
  const gest = (i: number) => 156 + i * 24;
  const activeB = [0, 1, 2, 3].reduce((a, i) => (f >= gest(i) ? i : a), -1);
  const armR: Arm = activeB >= 0 && f < 270
    ? {x: 900, y: 240 + activeB * 30, hand: 'pointUp', rot: -40 + Math.sin(f * 0.4) * 4}
    : {x: 1000, y: 700, hand: 'fist', flip: true};
  const armL: Arm = f < 40 ? {x: 300, y: 700, hand: 'fist'} : {x: 210, y: 420, hand: 'open', rot: -25, flip: true};
  return (
    <AbsoluteFill style={{background: C.ink}}>
      <PaperBg tone="dark" halftone={0.12} />
      <Rays cx={bx} cy={by} rot={f * 0.25} opacity={0.14 * bookIn} />
      <AbsoluteFill style={{background: `radial-gradient(circle at ${bx}px ${by}px, rgba(255,184,28,${0.35 * bookIn}) 0%, rgba(0,0,0,0) 45%)`}} />
      <KineticText text="E-BOOK" f={f - 18} mode="slam" x={540} y={150} size={70} color={C.ink} shadow={null} style={{background: C.amber, width: 260, left: 410, padding: '6px 0', border: `6px solid ${C.ink}`}} rotate={-3} />
      <KineticText text={BRAND.product} f={f - 26} mode="words" x={540} y={232} size={62} color={C.offWhite} stagger={3} highlight={{TIPU: C.red, JANGAN: C.amber, KENA: C.amber}} width={1000} />
      {/* comic panel that folds into the book */}
      {f < 13 ? (
        <AbsoluteFill style={{perspective: 2000}}>
          <div style={{position: 'absolute', left: 540 - 210, top: 720 - 300, width: 420, height: 600, background: C.cream, border: `10px solid ${C.ink}`, transform: `rotateY(${panelTurn}deg)`, boxShadow: `14px 14px 0 rgba(0,0,0,0.7)`}}>
            <Halftone opacity={0.2} color="#000" />
            <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: FONT.display, fontSize: 300, color: C.red}}>?</div>
          </div>
        </AbsoluteFill>
      ) : (
        <Book3D x={bx} y={by} w={bw} ry={ry} rx={6} rz={-3 + slide * 2} />
      )}
      {/* benefits */}
      {BRAND.benefits.map((b, i) => {
        const s = spr(f, gest(i), {damping: 11, stiffness: 170});
        if (f < gest(i)) return null;
        return (
          <div key={i} style={{position: 'absolute', left: 520, top: 430 + i * 136, width: 520, height: 112, transform: `translateX(${(1 - s) * 500}px) rotate(${(1 - s) * 8 + (i % 2 ? 1.5 : -1.5)}deg)`}}>
            <div style={{position: 'absolute', inset: 0, background: C.cream, border: `6px solid ${C.ink}`, boxShadow: `8px 8px 0 ${C.ink}`}} />
            <div style={{position: 'absolute', left: 16, top: 16, width: 80, height: 80, borderRadius: 40, background: C.amber, border: `5px solid ${C.ink}`}}>
              <svg width={70} height={70} viewBox="0 0 70 70">
                <path d="M 16 38 L 30 52 L 56 22" fill="none" stroke={C.ink} strokeWidth={10} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - ramp(f, gest(i) + 4, gest(i) + 12)} />
              </svg>
            </div>
            <div style={{position: 'absolute', left: 116, top: 0, height: 112, right: 10, display: 'flex', alignItems: 'center', fontFamily: FONT.sans, fontWeight: 800, fontSize: 38, lineHeight: 1.05, color: C.ink}}>{b}</div>
          </div>
        );
      })}
      <MrX
        x={250 + noise1(f * 0.05, 4) * 5}
        y={1900}
        height={620}
        expr={f < 150 ? 'normal' : 'gembira'}
        headRot={-6 + tk * 3}
        headY={-tk * 16}
        armR={f > 36 && f < 150 ? 70 + Math.sin(f * 0.2) * 4 : 10}
        armL={tk * 8}
        lean={f > 36 && f < 150 ? 3 : 0}
        blink={autoBlink(f, 71)}
        breathe={0.5 + 0.5 * Math.sin(f * 0.1)}
      />
      <XBot
        x={850}
        y={1880}
        height={470}
        expr={f < 156 ? 'love' : 'happy'}
        look={{x: -20, y: -16}}
        blink={autoBlink(f, 81, 70)}
        armR={armR}
        armL={armL}
        hop={activeB >= 0 && f < 270 ? Math.abs(Math.sin(((f - 156) / 24) * Math.PI)) * 30 : 0}
        capLift={f < 40 ? Math.max(0, Math.sin(f * 0.4) * 30) : 0}
      />
      <SpeechBubble id="L6" sceneFrom={from} x={30} y={1120} w={1020} tail={[300, 1330]} size={40} emphasis={['e-book', 'ringkas']} />
      <PageFlip p={flip}>
        <Halftone opacity={0.15} color="#000" />
      </PageFlip>
      <Grain opacity={0.14} />
    </AbsoluteFill>
  );
};
