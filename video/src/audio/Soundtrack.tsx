import React from 'react';
import {Audio, interpolate, Sequence} from 'remotion';
import {A, VO_ENABLED} from '../config/assets';
import {LINES} from '../config/script';

/**
 * Music + SFX mix. Score: original procedural composition (tools/compose_music.py) at 120 BPM so that
 * beats land on 15-frame multiples. SFX: synthesized (tools/synth_sfx.py) + Pixabay-licensed set (commercial OK).
 * Cue list = [frame, file, volume]. Edit freely; everything is frame-accurate.
 */
export const SFX: [number, string, number][] = [
  // 01 HOOK
  [0, 'whoosh-short.mp3', 0.55], [5, 'impact-bass-1.mp3', 0.9], [5, 'rumble.wav', 0.6], [9, 'ka_ching.wav', 0.45],
  [12, 'whip.wav', 0.4], [28, 'paper_rip.wav', 0.75], [33, 'boing.wav', 0.35], [40, 'pop.mp3', 0.5],
  [92, 'whoosh-short.mp3', 0.45], [96, 'stamp.wav', 0.35], [104, 'stamp.wav', 0.35], [108, 'record_scratch.wav', 0.8],
  [150, 'bot_chirp_1.wav', 0.3], [166, 'whoosh-cinematic.mp3', 0.55],
  // 02 MYTH
  [182, 'whip.wav', 0.4], [200, 'boing.wav', 0.4], [200, 'stamp.wav', 0.4], [206, 'bot_chirp_2.wav', 0.3],
  [236, 'whoosh.mp3', 0.4], [244, 'whoosh.mp3', 0.35], [266, 'bot_chirp_3.wav', 0.25], [292, 'servo.wav', 0.4],
  [300, 'impact-bass-2.mp3', 0.75], [308, 'marker.wav', 0.5], [424, 'whoosh-cinematic.mp3', 0.5],
  // 03 FACTORS
  [464, 'pop.mp3', 0.35], [471, 'pop.mp3', 0.35], [478, 'pop.mp3', 0.35], [485, 'pop.mp3', 0.35],
  [510, 'click.mp3', 0.45], [570, 'click.mp3', 0.45], [630, 'click.mp3', 0.45], [690, 'click.mp3', 0.45],
  [568, 'boing.wav', 0.25], [628, 'boing.wav', 0.25], [688, 'boing.wav', 0.25],
  [746, 'impact-bass-1.mp3', 0.6], [746, 'sparkle.mp3', 0.45], [776, 'whoosh-short.mp3', 0.4], [792, 'servo.wav', 0.35], [800, 'whip.wav', 0.45],
  // 04 CLAIMS
  [810, 'whoosh-cinematic.mp3', 0.45], [818, 'stamp.wav', 0.6], [850, 'marker.wav', 0.5], [862, 'tick.wav', 0.5],
  [880, 'tick.wav', 0.3], [888, 'marker.wav', 0.5], [910, 'glitch-1.mp3', 0.35], [926, 'marker.wav', 0.5],
  [950, 'error.mp3', 0.25], [964, 'marker.wav', 0.5], [1010, 'bot_chirp_1.wav', 0.25], [1132, 'whoosh.mp3', 0.4],
  [1146, 'stamp.wav', 0.8], [1146, 'impact-bass-2.mp3', 0.7], [1150, 'sparkle.mp3', 0.35], [1182, 'page_flip.wav', 0.6],
  // 05 E-BOOK
  [1200, 'whoosh-short.mp3', 0.4], [1212, 'page_flip.wav', 0.5], [1220, 'sparkle.mp3', 0.45], [1220, 'chime.mp3', 0.4],
  [1336, 'whoosh-short.mp3', 0.35], [1356, 'ping.mp3', 0.3], [1380, 'ping.mp3', 0.3], [1404, 'ping.mp3', 0.3], [1428, 'ping.mp3', 0.3],
  [1480, 'page_flip.wav', 0.6],
  // 06 CTA
  [1514, 'pop.mp3', 0.4], [1526, 'marker.wav', 0.5], [1530, 'bot_chirp_2.wav', 0.25], [1536, 'whoosh.mp3', 0.35],
  [1540, 'impact-bass-1.mp3', 0.8], [1541, 'ka_ching.wav', 0.55], [1600, 'pop.mp3', 0.45], [1640, 'chime.mp3', 0.45],
  [1668, 'stamp.wav', 0.5], [1680, 'sparkle.mp3', 0.4],
];

export const Soundtrack: React.FC = () => (
  <>
    <Audio
      src={A.music}
      volume={(f) => {
        const base = 0.5;
        if (!VO_ENABLED) return base;
        // duck music under recorded dialogue
        const speaking = LINES.some((l) => f >= l.from - 4 && f <= l.to + 4);
        return speaking ? base * 0.45 : base;
      }}
    />
    {SFX.map(([at, file, vol], i) => (
      <Sequence key={i} name={`SFX ${file}`} from={at} durationInFrames={90}>
        <Audio src={A.sfx(file)} volume={(f) => vol * interpolate(f, [70, 89], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} />
      </Sequence>
    ))}
  </>
);
