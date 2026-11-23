import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {MrX} from '../characters/MrX';
import {XBot} from '../characters/XBot';
export const RigTest: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: '#2a2830'}}>
      <MrX x={300} y={900} height={760} />
      <MrX x={780} y={900} height={760} armL={-30} armR={40} headRot={10} blink={1} />
      <XBot x={300} y={1750} height={600} expr="normal" />
      <XBot x={790} y={1750} height={600} expr="happy" armR={{x: 1100, y: 380, hand: 'pointUp', rot: 10}} armL={{x: 200, y: 520, hand: 'point', rot: 0, flip: true}} capLift={30} capTilt={-8} />
      <div style={{position: 'absolute', top: 20, left: 20, color: '#fff', fontSize: 30}}>{f}</div>
    </AbsoluteFill>
  );
};
