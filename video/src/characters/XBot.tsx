import React from 'react';
import {Img} from 'remotion';
import {A} from '../config/assets';

/**
 * X-BOT — living perfume bottle. Bottle/cap/gold neck redrawn as vector from the official hero render
 * (same silhouette, chamfered glossy body, gold rims, white sticker outline). Official raster parts:
 * gloves, sneakers, brush-X marks. Limbs are rubber-hose tubes (as in the design) so poses are free.
 * Coordinates = native px of the official hero image (ground y = 1088, centre x ~ 660).
 */
export type HandKind = 'fist' | 'thumb' | 'point' | 'pointUp' | 'open';
export type XBotExpr = 'normal' | 'happy' | 'surprised' | 'angry' | 'sad' | 'love' | 'squint' | 'closed';
export type Arm = {x: number; y: number; hand: HandKind; rot?: number; flip?: boolean; scale?: number};
export type XBotProps = {
  x: number;
  y: number;
  height: number;
  flip?: boolean;
  lean?: number;
  squash?: number;
  hop?: number; // native px up
  capLift?: number;
  capTilt?: number;
  expr?: XBotExpr;
  look?: {x: number; y: number};
  blink?: number;
  talk?: number; // 0..1 pulse
  glow?: number;
  armL?: Arm;
  armR?: Arm;
  footL?: {x: number; y: number; r?: number};
  footR?: {x: number; y: number; r?: number};
  opacity?: number;
  shadow?: boolean;
};

const HAND: Record<HandKind, {src: string; w: number; h: number; ax: number; ay: number}> = {
  fist: {src: A.xbot.hands.fist, w: 185, h: 229, ax: 0.8, ay: 0.12},
  thumb: {src: A.xbot.hands.thumb, w: 201, h: 275, ax: 0.88, ay: 0.82},
  point: {src: A.xbot.hands.point, w: 177, h: 195, ax: 0.1, ay: 0.72},
  pointUp: {src: A.xbot.hands.pointUp, w: 163, h: 199, ax: 0.5, ay: 0.96},
  open: {src: A.xbot.hands.open, w: 184, h: 190, ax: 0.5, ay: 0.94},
};
export const XB = {
  shoulderL: [356, 640] as const,
  shoulderR: [982, 615] as const,
  hipL: [480, 870] as const,
  hipR: [805, 870] as const,
  ground: 1088,
  cx: 662,
  top: 40,
};
export const XBOT_REST: {armL: Arm; armR: Arm} = {
  armL: {x: 330, y: 705, hand: 'fist', rot: 0},
  armR: {x: 1000, y: 700, hand: 'fist', rot: 0, flip: true},
};

const ch = 52; // body chamfer
const BODY = `M ${352 + ch} 328 L ${985 - ch} 328 L 985 ${328 + ch} L 985 ${888 - ch} L ${985 - ch} 888 L ${352 + ch} 888 L 352 ${888 - ch} L 352 ${328 + ch} Z`;

const Hose: React.FC<{from: readonly [number, number]; to: [number, number]; side: number; w?: number}> = ({from, to, side, w = 40}) => {
  const [x1, y1] = from;
  const [x2, y2] = to;
  const c1x = x1 + side * 95;
  const c1y = y1 + 25;
  const c2x = x2 + side * 20;
  const c2y = y2 + 70;
  const d = `M ${x1} ${y1} C ${c1x} ${c1y} ${c2x} ${c2y} ${x2} ${y2}`;
  return (
    <g fill="none" strokeLinecap="round">
      <path d={d} stroke="#fff" strokeWidth={w + 26} />
      <path d={d} stroke="#050506" strokeWidth={w + 8} />
      <path d={d} stroke="#1d1c21" strokeWidth={w - 4} />
      <path d={d} stroke="rgba(255,255,255,0.28)" strokeWidth={5} transform={`translate(${-side * 7},-6)`} />
    </g>
  );
};

const Hand: React.FC<{arm: Arm}> = ({arm}) => {
  const h = HAND[arm.hand];
  const sc = arm.scale ?? 1;
  const ax = arm.flip ? 1 - h.ax : h.ax;
  return (
    <image
      href={h.src}
      x={-h.w * ax}
      y={-h.h * h.ay}
      width={h.w}
      height={h.h}
      transform={`translate(${arm.x} ${arm.y}) rotate(${arm.rot ?? 0}) scale(${(arm.flip ? -1 : 1) * sc} ${sc})`}
      style={{transformBox: 'view-box'}}
      preserveAspectRatio="none"
    />
  );
};

const Eye: React.FC<{cx: number; cy: number; side: 1 | -1; expr: XBotExpr; blink: number; glow: number}> = ({cx, cy, side, expr, blink, glow}) => {
  const sY = Math.max(0.06, 1 - blink);
  const m = side; // mirror for right eye
  let shape: React.ReactNode;
  const fill = 'url(#xbEye)';
  if (expr === 'happy') {
    shape = <path d="M -70 22 Q 0 -62 70 22" stroke={fill} strokeWidth={26} fill="none" strokeLinecap="round" />;
  } else if (expr === 'surprised') {
    shape = (
      <>
        <circle r={56} fill={fill} />
        <circle r={27} fill="#160d02" />
      </>
    );
  } else if (expr === 'love') {
    shape = <path d="M 0 48 C -95 -10 -55 -78 0 -28 C 55 -78 95 -10 0 48 Z" fill="#ff5d8f" />;
  } else if (expr === 'closed') {
    shape = <path d="M -66 10 L 66 10" stroke={fill} strokeWidth={20} strokeLinecap="round" />;
  } else if (expr === 'sad') {
    shape = <path d={`M ${-74 * m} 6 L ${66 * m} -26 C ${58 * m} 40 ${0} 66 ${-40 * m} 52 C ${-66 * m} 40 ${-78 * m} 26 ${-74 * m} 6 Z`} fill={fill} />;
  } else {
    // normal / angry / squint: the official slanted "mischief" half-moon
    const k = expr === 'angry' ? 1.35 : 1;
    const sq = expr === 'squint' ? 0.55 : 1;
    shape = (
      <g transform={`scale(1 ${sq})`}>
        <path
          d={`M ${-80 * m} ${-34 * k} L ${74 * m} ${16 * k} C ${66 * m} 72 ${-6 * m} 92 ${-48 * m} 64 C ${-76 * m} 44 ${-84 * m} 10 ${-80 * m} ${-34 * k} Z`}
          fill={fill}
        />
        <path d={`M ${-58 * m} -6 L ${40 * m} 22 C ${30 * m} 50 ${-20 * m} 58 ${-42 * m} 40 Z`} fill="#fff3b0" opacity={0.55} />
      </g>
    );
  }
  return (
    <g transform={`translate(${cx} ${cy}) scale(1 ${sY})`}>
      <g filter="url(#xbGlow)" opacity={0.85 * glow}>
        {shape}
      </g>
      {shape}
    </g>
  );
};

export const XBot: React.FC<XBotProps> = ({
  x, y, height, flip = false, lean = 0, squash = 1, hop = 0, capLift = 0, capTilt = 0, expr = 'normal',
  look = {x: 0, y: 0}, blink = 0, talk = 0, glow = 1, armL = XBOT_REST.armL, armR = XBOT_REST.armR,
  footL = {x: 0, y: 0}, footR = {x: 0, y: 0}, opacity = 1, shadow = true,
}) => {
  const s = height / (XB.ground - XB.top);
  const sx = 1 / Math.sqrt(squash);
  const VW = 1312;
  const VH = 1199;
  const ankleL: [number, number] = [470 + footL.x, 945 + footL.y];
  const ankleR: [number, number] = [818 + footR.x, 945 + footR.y];
  return (
    <svg
      width={VW * s}
      height={VH * s}
      viewBox={`0 0 ${VW} ${VH}`}
      style={{position: 'absolute', left: x - XB.cx * s, top: y - XB.ground * s, overflow: 'visible', opacity, transform: flip ? 'scaleX(-1)' : undefined}}
    >
      <defs>
        <linearGradient id="xbBody" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#3b3a40" />
          <stop offset="0.35" stopColor="#141317" />
          <stop offset="1" stopColor="#050506" />
        </linearGradient>
        <radialGradient id="xbPanel" cx="0.45" cy="0.35" r="0.8">
          <stop offset="0" stopColor="#1a191d" />
          <stop offset="1" stopColor="#060607" />
        </radialGradient>
        <linearGradient id="xbGold" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stopColor="#6b4508" />
          <stop offset="0.25" stopColor="#ffd56a" />
          <stop offset="0.5" stopColor="#b77b14" />
          <stop offset="0.75" stopColor="#ffe08a" />
          <stop offset="1" stopColor="#7a4f0a" />
        </linearGradient>
        <linearGradient id="xbGoldV" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#ffd56a" stopOpacity="0" />
          <stop offset="0.3" stopColor="#ffc23d" />
          <stop offset="0.7" stopColor="#ff9d00" />
          <stop offset="1" stopColor="#ffc23d" stopOpacity="0" />
        </linearGradient>
        <linearGradient id="xbCap" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stopColor="#060607" />
          <stop offset="0.22" stopColor="#2d2c31" />
          <stop offset="0.3" stopColor="#d9d9de" />
          <stop offset="0.34" stopColor="#2a292e" />
          <stop offset="0.7" stopColor="#0b0b0d" />
          <stop offset="0.9" stopColor="#5e5d64" />
          <stop offset="1" stopColor="#0a0a0b" />
        </linearGradient>
        <radialGradient id="xbEye" cx="0.5" cy="0.45" r="0.6">
          <stop offset="0" stopColor="#ffe36b" />
          <stop offset="0.6" stopColor="#ffc21a" />
          <stop offset="1" stopColor="#ff9200" />
        </radialGradient>
        <filter id="xbGlow" x="-1" y="-1" width="3" height="3">
          <feGaussianBlur stdDeviation="16" />
        </filter>
        <filter id="xbSoft" x="-1" y="-1" width="3" height="3">
          <feGaussianBlur stdDeviation="14" />
        </filter>
      </defs>
      {shadow ? <ellipse cx={660} cy={1090} rx={380 * (1 - Math.min(hop, 300) / 600)} ry={34} fill="rgba(0,0,0,0.5)" filter="url(#xbSoft)" /> : null}
      <g transform={`rotate(${lean} 660 1088) translate(660 1088) scale(${sx} ${squash}) translate(-660 -1088) translate(0 ${-hop})`}>
        {/* legs */}
        <Hose from={XB.hipL} to={ankleL} side={-0.4} w={44} />
        <Hose from={XB.hipR} to={ankleR} side={0.4} w={44} />
        <image href={A.xbot.shoeL} x={271.5 + footL.x} y={903.5 + footL.y} width={327} height={205} transform={`rotate(${footL.r ?? 0} ${ankleL[0]} ${ankleL[1]})`} />
        <image href={A.xbot.shoeR} x={703.5 + footR.x} y={903.5 + footR.y} width={326} height={204} transform={`rotate(${footR.r ?? 0} ${ankleR[0]} ${ankleR[1]})`} />
        {/* arm hoses (behind body) */}
        <Hose from={XB.shoulderL} to={[armL.x, armL.y]} side={-1} />
        <Hose from={XB.shoulderR} to={[armR.x, armR.y]} side={1} />
        {/* body */}
        <path d={BODY} fill="none" stroke="#fff" strokeWidth={34} strokeLinejoin="round" />
        <path d={BODY} fill="url(#xbBody)" stroke="#050506" strokeWidth={12} strokeLinejoin="round" />
        <path d={`M 945 ${328 + 8} L 977 ${328 + ch - 6} L 977 ${888 - ch + 6} L 945 ${888 - 8} Z`} fill="#0b0b0d" />
        <path d={`M 946 400 L 946 830`} stroke="url(#xbGoldV)" strokeWidth={7} />
        <path d={`M 361 395 L 361 830`} stroke="url(#xbGoldV)" strokeWidth={8} />
        <path d={`M ${352 + ch + 6} 338 L 520 338 L 410 420 L 362 ${328 + ch + 30} Z`} fill="rgba(255,255,255,0.32)" />
        <path d={`M ${985 - ch - 4} 336 L 975 ${328 + ch} `} stroke="#ffcf5a" strokeWidth={6} opacity={0.8} />
        <rect x={408} y={392} width={478} height={444} rx={34} fill="url(#xbPanel)" stroke="#2b2a30" strokeWidth={7} />
        <rect x={420} y={404} width={454} height={420} rx={26} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={3} />
        <path d="M 432 420 L 640 420 L 560 470 L 432 520 Z" fill="rgba(255,255,255,0.05)" />
        {/* face: eyes + official brush X */}
        <g transform={`translate(${look.x} ${look.y})`}>
          <Eye cx={528} cy={532} side={1} expr={expr} blink={blink} glow={glow} />
          <Eye cx={768} cy={532} side={-1} expr={expr} blink={blink} glow={glow} />
          {expr === 'sad' ? (
            <g fill="#5fc3ff">
              <path d="M 470 600 q -16 34 0 44 q 16 -10 0 -44 Z" />
              <path d="M 826 600 q -16 34 0 44 q 16 -10 0 -44 Z" />
            </g>
          ) : null}
        </g>
        <image
          href={A.xbot.markFace}
          x={641 - 143.5}
          y={700 - 106}
          width={287}
          height={212}
          transform={`translate(641 700) scale(${1 + talk * 0.07} ${1 - talk * 0.09}) translate(-641 -700)`}
        />
        {/* neck + cap */}
        <g transform={`translate(0 ${-capLift}) rotate(${capTilt} 660 300)`}>
          <rect x={540} y={236} width={246} height={74} rx={10} fill="#0b0b0d" stroke="#fff" strokeWidth={10} paintOrder="stroke" />
          <rect x={540} y={236} width={246} height={74} rx={10} fill="#0d0d0f" stroke="#050506" strokeWidth={6} />
          <rect x={560} y={244} width={16} height={58} fill="rgba(255,255,255,0.3)" />
          <rect x={548} y={298} width={230} height={40} rx={8} fill="url(#xbGold)" stroke="#2a1a02" strokeWidth={5} />
          <rect x={548} y={306} width={230} height={6} fill="rgba(255,255,255,0.45)" />
          <path d="M 468 80 L 468 238 A 192 38 0 0 0 852 238 L 852 80 Z" fill="none" stroke="#fff" strokeWidth={30} strokeLinejoin="round" />
          <ellipse cx={660} cy={80} rx={192} ry={38} fill="none" stroke="#fff" strokeWidth={30} />
          <path d="M 468 80 L 468 238 A 192 38 0 0 0 852 238 L 852 80 Z" fill="url(#xbCap)" stroke="#050506" strokeWidth={10} />
          <ellipse cx={660} cy={80} rx={192} ry={38} fill="#141317" stroke="#050506" strokeWidth={10} />
          <ellipse cx={640} cy={74} rx={140} ry={18} fill="rgba(255,255,255,0.12)" />
          <image href={A.xbot.markCap} x={660 - 80} y={160 - 70} width={160} height={140} />
        </g>
        {/* hands in front */}
        <Hand arm={armL} />
        <Hand arm={armR} />
      </g>
    </svg>
  );
};
