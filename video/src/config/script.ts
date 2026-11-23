// Dialogue = single source of truth for speech bubbles, subtitles (SRT) and VO slots.
// Frames are absolute (30 fps). `vo` = optional recorded file in public/audio/vo/ (set VO_ENABLED in assets.ts).
export type Speaker = 'MRX' | 'XBOT';
export type Line = {id: string; speaker: Speaker; from: number; to: number; text: string; vo: string};
export const LINES: Line[] = [
  {id: 'L1', speaker: 'MRX', from: 44, to: 150, text: 'Perfume lapan ratus ringgit? Mesti tahan lama gila, kan?!', vo: 'L1_mrx.wav'},
  {id: 'L2', speaker: 'XBOT', from: 206, to: 262, text: 'Eh, belum tentu!', vo: 'L2_xbot.wav'},
  {id: 'L3', speaker: 'XBOT', from: 266, to: 420, text: 'Harga mahal bukan jaminan perfume lebih tahan lama!', vo: 'L3_xbot.wav'},
  {id: 'L4', speaker: 'MRX', from: 560, to: 790, text: 'Ohh, jadi bukan harga saja! Formula, bahan, kulit dan keadaan sekeliling pun memainkan peranan!', vo: 'L4_mrx.wav'},
  {id: 'L5', speaker: 'XBOT', from: 1010, to: 1170, text: 'Sebab tu kena faham asas perfume. Jangan terus percaya claim seller tanpa tahu apa yang kau beli!', vo: 'L5_xbot.wav'},
  {id: 'L6', speaker: 'MRX', from: 1236, to: 1400, text: 'Kalau kau nak belajar sebelum membeli, aku dah sediakan e-book ringkas untuk kau.', vo: 'L6_mrx.wav'},
  {id: 'L7', speaker: 'XBOT', from: 1530, to: 1660, text: 'RM10.90 je! Belajar dulu, baru beli dengan yakin!', vo: 'L7_xbot.wav'},
];
