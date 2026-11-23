import React from 'react';
import {Audio, Sequence} from 'remotion';
import {A, VO_ENABLED} from '../config/assets';
import {LINES} from '../config/script';

/** Voice-over slots. Recorded files go to public/audio/vo/<line.vo>; flip VO_ENABLED in config/assets.ts. */
export const Dialogue: React.FC = () => {
  if (!VO_ENABLED) return null;
  return (
    <>
      {LINES.map((l) => (
        <Sequence key={l.id} name={`VO ${l.id} ${l.speaker}`} from={l.from} durationInFrames={l.to - l.from + 30}>
          <Audio src={A.vo(l.vo)} volume={1} />
        </Sequence>
      ))}
    </>
  );
};
