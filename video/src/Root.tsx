import React from 'react';
import {Composition} from 'remotion';
import {Perfume101} from './compositions/Perfume101';
import {RigTest} from './compositions/RigTest';
import {FPS, H, TOTAL, W} from './config/timeline';
export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Perfume101" component={Perfume101} durationInFrames={TOTAL} fps={FPS} width={W} height={H} defaultProps={{audio: true}} />
    <Composition id="RigTest" component={RigTest} durationInFrames={30} fps={FPS} width={W} height={H} />
  </>
);
