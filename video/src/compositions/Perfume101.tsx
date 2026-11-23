import React from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {Soundtrack} from '../audio/Soundtrack';
import {Dialogue} from '../audio/Dialogue';
import {loadAllFonts} from '../components/Fonts';
import {C} from '../config/brand';
import {SCENES} from '../config/timeline';
import {Claims} from '../scenes/Claims';
import {EbookReveal} from '../scenes/EbookReveal';
import {Factors} from '../scenes/Factors';
import {FinalCTA} from '../scenes/FinalCTA';
import {Hook} from '../scenes/Hook';
import {Myth} from '../scenes/Myth';

loadAllFonts();

export const Perfume101: React.FC<{audio?: boolean}> = ({audio = true}) => (
  <AbsoluteFill style={{background: C.ink}}>
    <Sequence name="01 Hook" from={SCENES.hook.from} durationInFrames={SCENES.hook.dur}>
      <Hook />
    </Sequence>
    <Sequence name="02 Myth" from={SCENES.myth.from} durationInFrames={SCENES.myth.dur}>
      <Myth />
    </Sequence>
    <Sequence name="03 Factors" from={SCENES.factors.from} durationInFrames={SCENES.factors.dur}>
      <Factors />
    </Sequence>
    <Sequence name="04 Claims" from={SCENES.claims.from} durationInFrames={SCENES.claims.dur}>
      <Claims />
    </Sequence>
    <Sequence name="05 E-book" from={SCENES.ebook.from} durationInFrames={SCENES.ebook.dur}>
      <EbookReveal />
    </Sequence>
    <Sequence name="06 CTA" from={SCENES.cta.from} durationInFrames={SCENES.cta.dur}>
      <FinalCTA />
    </Sequence>
    {audio ? (
      <>
        <Soundtrack />
        <Dialogue />
      </>
    ) : null}
  </AbsoluteFill>
);
