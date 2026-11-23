import React from 'react';
import {Img} from 'remotion';
import {A} from '../config/assets';
import {BRAND, C, FONT} from '../config/brand';
import {rnd} from '../lib/anim';

/** Fictional, unbranded perfume bottles (vector). */
export const PerfumeBottle: React.FC<{variant: 'luxe' | 'basic'; x: number; y: number; h: number; rot?: number; shine?: number; liquid?: number; style?: React.CSSProperties}> = ({
  variant, x, y, h, rot = 0, shine = 0, liquid = 1, style,
}) => {
  const s = h / 560;
  const id = `pb${variant}`;
  return (
    <svg width={400 * s} height={600 * s} viewBox="0 0 400 600" style={{position: 'absolute', left: x - 200 * s, top: y - 560 * s, overflow: 'visible', transform: `rotate(${rot}deg)`, transformOrigin: '50% 93%', ...style}}>
      <defs>
        <linearGradient id={`${id}glass`} x1="0" x2="1">
          <stop offset="0" stopColor={variant === 'luxe' ? '#3a2306' : '#d9e6ea'} stopOpacity={variant === 'luxe' ? 1 : 0.55} />
          <stop offset="0.45" stopColor={variant === 'luxe' ? '#b86b0c' : '#f4fbff'} stopOpacity={variant === 'luxe' ? 1 : 0.35} />
          <stop offset="1" stopColor={variant === 'luxe' ? '#2a1704' : '#b9cdd3'} stopOpacity={variant === 'luxe' ? 1 : 0.6} />
        </linearGradient>
        <linearGradient id={`${id}liq`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor={variant === 'luxe' ? '#ffcb5c' : '#ffe9a8'} />
          <stop offset="1" stopColor={variant === 'luxe' ? '#c46f00' : '#f5c96b'} />
        </linearGradient>
        <linearGradient id={`${id}gold`} x1="0" x2="1">
          <stop offset="0" stopColor="#6b4508" />
          <stop offset="0.3" stopColor="#ffe08a" />
          <stop offset="0.55" stopColor="#b77b14" />
          <stop offset="0.8" stopColor="#ffd56a" />
          <stop offset="1" stopColor="#6b4508" />
        </linearGradient>
        <linearGradient id={`${id}silver`} x1="0" x2="1">
          <stop offset="0" stopColor="#6d7378" />
          <stop offset="0.35" stopColor="#f3f6f8" />
          <stop offset="0.7" stopColor="#9aa1a6" />
          <stop offset="1" stopColor="#5b6166" />
        </linearGradient>
      </defs>
      <ellipse cx={200} cy={566} rx={170} ry={22} fill="rgba(0,0,0,0.5)" />
      {variant === 'luxe' ? (
        <g stroke={C.ink} strokeWidth={9} strokeLinejoin="round">
          {/* faceted body */}
          <path d="M 60 250 L 110 200 L 290 200 L 340 250 L 340 520 L 300 560 L 100 560 L 60 520 Z" fill={`url(#${id}glass)`} />
          <path d={`M 80 ${520 - 270 * liquid} L 320 ${520 - 270 * liquid} L 320 515 L 292 543 L 108 543 L 80 515 Z`} fill={`url(#${id}liq)`} stroke="none" opacity={0.92} />
          <path d="M 110 200 L 140 250 L 260 250 L 290 200 M 140 250 L 140 520 L 100 560 M 260 250 L 260 520 L 300 560 M 140 520 L 260 520" fill="none" stroke="rgba(0,0,0,0.45)" strokeWidth={5} />
          <rect x={120} y={330} width={160} height={110} fill="#f3e6c9" stroke={C.ink} strokeWidth={6} />
          <rect x={160} y={150} width={80} height={55} fill={`url(#${id}gold)`} />
          <path d="M 110 30 L 290 30 L 320 80 L 290 150 L 110 150 L 80 80 Z" fill="#111015" />
          <path d="M 110 30 L 290 30 L 320 80 L 80 80 Z" fill="#2a2930" />
          <path d="M 80 80 L 320 80" stroke={`url(#${id}gold)`} strokeWidth={10} />
        </g>
      ) : (
        <g stroke={C.ink} strokeWidth={9} strokeLinejoin="round">
          <rect x={85} y={230} width={230} height={330} rx={44} fill={`url(#${id}glass)`} />
          <rect x={98} y={230 + 320 * (1 - liquid * 0.85)} width={204} height={316 * liquid * 0.85} rx={34} fill={`url(#${id}liq)`} stroke="none" opacity={0.85} />
          <rect x={160} y={175} width={80} height={60} rx={8} fill={`url(#${id}silver)`} />
          <rect x={140} y={95} width={120} height={85} rx={14} fill={`url(#${id}silver)`} />
          <rect x={130} y={330} width={140} height={90} rx={10} fill="#fffdf6" stroke={C.ink} strokeWidth={6} />
        </g>
      )}
      <text x={200} y={variant === 'luxe' ? 396 : 384} textAnchor="middle" fontFamily="Montserrat" fontWeight={800} fontSize={26} fill={C.ink} letterSpacing="3">
        PARFUM
      </text>
      <text x={200} y={variant === 'luxe' ? 424 : 408} textAnchor="middle" fontFamily="Montserrat" fontWeight={600} fontSize={15} fill="#555" letterSpacing="4">
        {variant === 'luxe' ? 'EAU DE PARFUM' : 'EAU DE TOILETTE'}
      </text>
      {/* glass highlight */}
      <path d={variant === 'luxe' ? 'M 84 270 L 84 500' : 'M 108 280 L 108 520'} stroke="#fff" strokeWidth={10} strokeLinecap="round" opacity={0.55} />
      {shine > 0 ? <rect x={-200 + shine * 700} y={0} width={60} height={600} fill="#fff" opacity={0.35} transform="skewX(-20)" style={{mixBlendMode: 'overlay'}} /> : null}
    </svg>
  );
};

/** Swinging price tag on a string. (x,y) = string anchor. */
export const PriceTag: React.FC<{x: number; y: number; text: string; swing: number; scale?: number; color?: string; strike?: number}> = ({x, y, text, swing, scale = 1, color = C.red, strike = 0}) => (
  <div style={{position: 'absolute', left: x, top: y, transformOrigin: '0 0', transform: `scale(${scale}) rotate(${swing}deg)`}}>
    <svg width={460} height={330} style={{position: 'absolute', left: -40, top: -20, overflow: 'visible'}}>
      <path d="M 40 20 Q 60 70 110 110" stroke={C.paper} strokeWidth={5} fill="none" />
      <g transform="translate(70 90) rotate(-12)">
        <path d="M 0 60 L 60 0 L 360 0 L 360 160 L 60 160 Z" fill={C.cream} stroke={C.ink} strokeWidth={9} strokeLinejoin="round" transform="translate(8 10)" opacity={0.6} />
        <path d="M 0 60 L 60 0 L 360 0 L 360 160 L 60 160 Z" fill={C.cream} stroke={C.ink} strokeWidth={9} strokeLinejoin="round" />
        <circle cx={48} cy={62} r={13} fill={C.charcoal} stroke={C.ink} strokeWidth={5} />
        <text x={215} y={115} textAnchor="middle" fontFamily="Bangers" fontSize={104} fill={color} stroke={C.ink} strokeWidth={4} paintOrder="stroke" letterSpacing="2">
          {text}
        </text>
        {strike > 0 ? <path d={`M 80 ${100} L ${80 + 260 * strike} ${60}`} stroke={C.ink} strokeWidth={16} strokeLinecap="round" /> : null}
      </g>
    </svg>
  </div>
);

/** Rubber stamp. */
export const Stamp: React.FC<{x: number; y: number; text: string; p: number; color?: string; rot?: number; size?: number; sub?: string}> = ({x, y, text, p, color = C.red, rot = -10, size = 150, sub}) => {
  if (p <= 0) return null;
  const sc = 1 + (1 - Math.min(1, p)) * 1.6;
  return (
    <div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%,-50%) rotate(${rot}deg) scale(${sc})`, opacity: Math.min(1, p * 1.5)}}>
      <div style={{border: `12px solid ${color}`, borderRadius: 22, padding: '6px 34px 0', color, fontFamily: FONT.display, fontSize: size, lineHeight: 1, letterSpacing: '0.04em', whiteSpace: 'nowrap', textAlign: 'center', boxShadow: `inset 0 0 0 5px ${C.paper}, 0 0 0 4px ${C.paper}`, background: 'rgba(239,230,212,0.08)', WebkitMaskImage: 'radial-gradient(circle at 30% 40%, black 60%, rgba(0,0,0,0.75) 100%)'}}>
        {text}
        {sub ? <div style={{fontFamily: FONT.sans, fontWeight: 800, fontSize: size * 0.2, letterSpacing: '0.3em', paddingBottom: 10}}>{sub}</div> : null}
      </div>
    </div>
  );
};

/** Ink splatter dots around a point. */
export const Splatter: React.FC<{cx: number; cy: number; p: number; color?: string; n?: number; r?: number; seed?: number}> = ({cx, cy, p, color = C.red, n = 16, r = 260, seed = 5}) => (
  <svg width={1080} height={1920} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
    {Array.from({length: n}).map((_, i) => {
      const a = rnd(i + seed) * Math.PI * 2;
      const d = (0.5 + rnd(i * 3 + seed) * 0.6) * r * Math.min(1, p * 1.4);
      return <circle key={i} cx={cx + Math.cos(a) * d} cy={cy + Math.sin(a) * d} r={(4 + rnd(i * 7 + seed) * 16) * Math.min(1, p * 2)} fill={color} />;
    })}
  </svg>
);

/**
 * E-BOOK COVER. The official cover was not supplied, so this is an editable stand-in built only from the
 * brand system (title text, brand marks, official characters). Supply A.ebookCover to use the real one.
 */
export const EbookCover: React.FC<{w: number; h: number}> = ({w, h}) => {
  if (A.ebookCover) return <Img src={A.ebookCover} style={{width: w, height: h, objectFit: 'cover', display: 'block'}} />;
  const s = w / 600;
  return (
    <div style={{width: w, height: h, position: 'relative', overflow: 'hidden', background: `linear-gradient(160deg, #1d1b21, #0b0a0c)`}}>
      <div style={{position: 'absolute', inset: 0, opacity: 0.12, backgroundImage: 'radial-gradient(#fff 22%, transparent 24%)', backgroundSize: `${12 * s}px ${12 * s}px`}} />
      <div style={{position: 'absolute', left: -60 * s, top: 420 * s, width: 800 * s, height: 260 * s, background: C.amber, transform: 'rotate(-8deg)'}} />
      <Img src={A.brand.wordmark} style={{position: 'absolute', left: 40 * s, top: 40 * s, width: 330 * s}} />
      <div style={{position: 'absolute', left: 40 * s, top: 130 * s, padding: `${4 * s}px ${14 * s}px`, background: C.offWhite, color: C.ink, fontFamily: FONT.display, fontSize: 34 * s, letterSpacing: '0.08em'}}>{BRAND.series} · E-BOOK</div>
      <div style={{position: 'absolute', left: 40 * s, top: 200 * s, width: 520 * s, fontFamily: FONT.display, fontSize: 92 * s, lineHeight: 0.95, color: C.offWhite, textShadow: `${5 * s}px ${5 * s}px 0 ${C.ink}`}}>
        SEBELUM BELI PERFUME,
      </div>
      <div style={{position: 'absolute', left: 30 * s, top: 455 * s, width: 560 * s, fontFamily: FONT.display, fontSize: 104 * s, lineHeight: 0.9, color: C.ink, transform: 'rotate(-8deg)'}}>
        JANGAN KENA TIPU!
      </div>
      <Img src={A.mrx.thumbChin} style={{position: 'absolute', right: -10 * s, bottom: -40 * s, height: 400 * s}} />
      <div style={{position: 'absolute', left: 40 * s, bottom: 60 * s, width: 300 * s, fontFamily: FONT.sans, fontWeight: 700, fontSize: 22 * s, lineHeight: 1.35, color: C.paper}}>
        Panduan ringkas untuk pembeli perfume
      </div>
      <div style={{position: 'absolute', inset: 0, boxShadow: `inset 0 0 0 ${8 * s}px ${C.ink}`}} />
    </div>
  );
};

/** 3D book (CSS 3D, deterministic). */
export const Book3D: React.FC<{x: number; y: number; w: number; ry: number; rx?: number; rz?: number; open?: number; style?: React.CSSProperties}> = ({x, y, w, ry, rx = 0, rz = 0, open = 0, style}) => {
  const h = w * 1.42;
  const d = w * 0.09;
  return (
    <div style={{position: 'absolute', left: x - w / 2, top: y - h / 2, width: w, height: h, perspective: 2400, ...style}}>
      <div style={{position: 'absolute', inset: 0, transformStyle: 'preserve-3d', transform: `rotateX(${rx}deg) rotateY(${ry}deg) rotateZ(${rz}deg)`}}>
        {/* back cover */}
        <div style={{position: 'absolute', inset: 0, background: '#0c0b0e', transform: `translateZ(${-d / 2}px)`, boxShadow: '0 40px 80px rgba(0,0,0,0.6)'}} />
        {/* pages block */}
        <div style={{position: 'absolute', top: 6, bottom: 6, right: 0, width: d, background: 'repeating-linear-gradient(90deg,#f3ead8 0 3px,#d9cdb5 3px 4px)', transformOrigin: 'right center', transform: `rotateY(90deg) translateX(${d / 2}px)`}} />
        {/* spine */}
        <div style={{position: 'absolute', top: 0, bottom: 0, left: 0, width: d, background: '#1a181d', transformOrigin: 'left center', transform: `rotateY(-90deg) translateX(${-d / 2}px)`}} />
        {/* inner page (visible when opened) */}
        <div style={{position: 'absolute', inset: 6, background: C.cream, transform: `translateZ(${d / 2 - 2}px)`}} />
        {/* front cover hinged on the left */}
        <div style={{position: 'absolute', inset: 0, transformOrigin: 'left center', transform: `translateZ(${d / 2}px) rotateY(${-open * 150}deg)`, backfaceVisibility: 'hidden'}}>
          <EbookCover w={w} h={h} />
          <div style={{position: 'absolute', inset: 0, background: `linear-gradient(${100 + ry}deg, rgba(255,255,255,0.0) 30%, rgba(255,255,255,0.22) 48%, rgba(255,255,255,0) 60%)`}} />
        </div>
      </div>
    </div>
  );
};
