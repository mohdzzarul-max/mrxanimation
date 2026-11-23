import React from 'react';
import {Img} from 'remotion';
import {A} from '../config/assets';
import rig from '../../public/characters/mrx/rig.json';
import poses from '../../public/characters/mrx/poses/poses.json';

/**
 * MR X — cut-out rig built from the official front turnaround (4x upscaled).
 * Layer stack (back -> front): shadow, body(torso+legs), armL, armR, sleeveL, sleeveR, shirt emblem, head (+eye lids).
 * All transforms are pure functions of props -> deterministic per frame.
 */
export type MrXExpr = 'normal' | 'biasa' | 'gembira' | 'terkejut' | 'marah' | 'malu' | 'fikir';
export type MrXView = 'front' | '34' | 'side' | 'back' | 'thumbChin';
export type MrXProps = {
  x: number; // ground point (between feet) in composition px
  y: number;
  height: number; // full character height in px
  view?: MrXView;
  flip?: boolean;
  headRot?: number;
  headX?: number; // in rig px (4x canvas)
  headY?: number;
  headScale?: number;
  armL?: number; // deg, + = outward/up (viewer's left arm)
  armR?: number; // deg, + = outward/up (viewer's right arm)
  lean?: number; // deg around feet
  squash?: number; // 1 = neutral; >1 taller
  breathe?: number; // 0..1
  expr?: MrXExpr;
  blink?: number; // 0..1
  shadow?: boolean;
  opacity?: number;
  emblem?: boolean;
  style?: React.CSSProperties;
};

const CW = rig.canvas.w;
const CH = rig.canvas.h;
const GROUND = 2790;
const L = rig.layers;
const P = rig.pivots;
const HC = rig.headCircle;

const layer = (key: keyof typeof L, src: string, extra?: React.CSSProperties) => (
  <Img
    src={src}
    style={{position: 'absolute', left: L[key].x, top: L[key].y, width: L[key].w, height: L[key].h, ...extra}}
  />
);

const POSE_SRC: Record<keyof typeof poses, string> = {
  gembira: A.mrx.poses.gembira,
  terkejut: A.mrx.poses.terkejut,
  marah: A.mrx.poses.marah,
  malu: A.mrx.poses.malu,
  fikir: A.mrx.poses.fikir,
};

const SPRITE: Record<Exclude<MrXView, 'front'>, {src: string; h: number}> = {
  '34': {src: A.mrx.view34, h: 2813},
  side: {src: A.mrx.viewSide, h: 2807},
  back: {src: A.mrx.viewBack, h: 2804},
  thumbChin: {src: A.mrx.thumbChin, h: 1780},
};

export const MrX: React.FC<MrXProps> = ({
  x, y, height, view = 'front', flip = false, headRot = 0, headX = 0, headY = 0, headScale = 1,
  armL = 0, armR = 0, lean = 0, squash = 1, breathe = 0, expr = 'normal', blink = 0, shadow = true,
  opacity = 1, emblem = true, style,
}) => {
  const s = height / 2760;
  const uid = React.useId().replace(/:/g, '');
  const sq = squash * (1 + breathe * 0.012);
  const sx = 1 / Math.sqrt(sq);
  const poseKey = expr === 'normal' || expr === 'biasa' ? null : (expr as keyof typeof poses);

  const shadowEl = shadow ? (
    <div
      style={{
        position: 'absolute', left: CW / 2 - 560, top: GROUND - 70, width: 1120, height: 140, borderRadius: '50%',
        background: 'radial-gradient(closest-side, rgba(0,0,0,0.55), rgba(0,0,0,0))',
        transform: `scaleX(${1 / sx})`,
      }}
    />
  ) : null;

  let inner: React.ReactNode;
  if (view === 'front' && poseKey) {
    // official full-body expression pose, scaled so its head matches the rig head, feet on the ground
    const P2 = poses[poseKey];
    const k = HC.r / P2.headR;
    const h = P2.h * k;
    const w = P2.w * k;
    const left = CW / 2 - P2.headCx * k + headX * 0.6;
    inner = (
      <div style={{position: 'absolute', left: 0, top: 0, width: CW, height: CH, transformOrigin: `${CW / 2}px ${GROUND}px`, transform: `rotate(${lean + headRot * 0.35}deg) scale(${sx * headScale},${sq * headScale}) translateY(${headY * 0.5}px)`}}>
        <Img src={POSE_SRC[poseKey]} style={{position: 'absolute', left, top: GROUND - h + 14 * k, width: w, height: h}} />
      </div>
    );
  } else if (view !== 'front') {
    const sp = SPRITE[view];
    const k = 2760 / sp.h; // normalise sprite height to rig height
    inner = (
      <div style={{position: 'absolute', left: 0, top: 0, width: CW, height: CH, transformOrigin: `${CW / 2}px ${GROUND}px`, transform: `rotate(${lean}deg) scale(${sx},${sq})`}}>
        <Img
          src={sp.src}
          style={{position: 'absolute', height: sp.h * k, left: CW / 2, top: GROUND - sp.h * k + 10, transform: 'translateX(-50%)'}}
        />
      </div>
    );
  } else {
    const arm = (key: 'armL' | 'armR', deg: number) => (
      <div style={{position: 'absolute', inset: 0, transformOrigin: `${P[key][0]}px ${P[key][1]}px`, transform: `rotate(${key === 'armL' ? deg : -deg}deg)`}}>
        {layer(key, A.mrx[key])}
      </div>
    );
    const eyesTop = Math.min(...rig.eyes.map((e) => e.y0)) - L.head.y;
    const eyesBot = Math.max(...rig.eyes.map((e) => e.y1)) - L.head.y;
    inner = (
      <div style={{position: 'absolute', left: 0, top: 0, width: CW, height: CH, transformOrigin: `${CW / 2}px ${GROUND}px`, transform: `rotate(${lean}deg) scale(${sx},${sq})`}}>
        {layer('body', A.mrx.body)}
        {arm('armL', armL)}
        {arm('armR', armR)}
        {layer('sleeveL', A.mrx.sleeveL)}
        {layer('sleeveR', A.mrx.sleeveR)}
        {emblem ? (
          <Img src={A.xbot.markFace} style={{position: 'absolute', left: 682 - 78, top: 1585, width: 156, opacity: 0.95, transform: 'rotate(-4deg)'}} />
        ) : null}
        <div
          style={{
            position: 'absolute', inset: 0, transformOrigin: `${P.head[0]}px ${P.head[1]}px`,
            transform: `translate(${headX}px, ${headY}px) rotate(${headRot}deg) scale(${headScale})`,
          }}
        >
          {(
            <>
              {layer('head', A.mrx.head)}
              {blink > 0.02 ? (
                <svg width={CW} height={CH} style={{position: 'absolute', left: 0, top: 0}} viewBox={`0 0 ${CW} ${CH}`}>
                  <defs>
                    <clipPath id={`mrxEye${uid}`}>
                      {rig.eyeClip.map((d, i) => (
                        <path key={i} d={d} />
                      ))}
                    </clipPath>
                    <linearGradient id={`mrxLid${uid}`} x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0" stopColor="#d98e6a" />
                      <stop offset="0.7" stopColor="#f6c3a0" />
                      <stop offset="1" stopColor="#efb08a" />
                    </linearGradient>
                  </defs>
                  <g clipPath={`url(#mrxEye${uid})`}>
                    <rect x={0} y={eyesTop + L.head.y - 40} width={CW} height={40 + (eyesBot - eyesTop) * 0.86 * blink} fill={`url(#mrxLid${uid})`} />
                    <rect x={0} y={eyesTop + L.head.y + (eyesBot - eyesTop) * 0.86 * blink - 6} width={CW} height={24} fill="#0d0c0e" />
                  </g>
                </svg>
              ) : null}
            </>
          )}
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        position: 'absolute', left: x - (CW * s) / 2, top: y - GROUND * s, width: CW, height: CH,
        transformOrigin: '0 0', transform: `scale(${s * (flip ? -1 : 1)}, ${s})${flip ? ` translateX(${-CW}px)` : ''}`,
        opacity, ...style,
      }}
    >
      {shadowEl}
      {inner}
    </div>
  );
};
