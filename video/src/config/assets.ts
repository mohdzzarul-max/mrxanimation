import {staticFile} from 'remotion';
// Asset manifest. Every official asset was extracted from the uploaded reference sheets (see ASSET_MANIFEST.md).
export const A = {
  mrx: {
    rig: staticFile('characters/mrx/rig.json'),
    head: staticFile('characters/mrx/head.png'),
    body: staticFile('characters/mrx/body.png'),
    armL: staticFile('characters/mrx/armL.png'),
    armR: staticFile('characters/mrx/armR.png'),
    sleeveL: staticFile('characters/mrx/sleeveL.png'),
    sleeveR: staticFile('characters/mrx/sleeveR.png'),
    eyeMask: staticFile('characters/mrx/eyeMask.png'),
    view34: staticFile('characters/mrx/mrx_34.png'),
    viewSide: staticFile('characters/mrx/mrx_side.png'),
    viewBack: staticFile('characters/mrx/mrx_back.png'),
    thumbChin: staticFile('characters/mrx/poses/thumb_chin.png'),
    heads: {
      biasa: staticFile('characters/mrx/heads/biasa.png'),
      gembira: staticFile('characters/mrx/heads/gembira.png'),
      terkejut: staticFile('characters/mrx/heads/terkejut.png'),
      marah: staticFile('characters/mrx/heads/marah.png'),
      malu: staticFile('characters/mrx/heads/malu.png'),
      fikir: staticFile('characters/mrx/heads/fikir.png'),
    },
  },
  xbot: {
    shoeL: staticFile('characters/xbot/shoeL.png'),
    shoeR: staticFile('characters/xbot/shoeR.png'),
    markFace: staticFile('characters/xbot/markFace.png'),
    markCap: staticFile('characters/xbot/markCap.png'),
    hands: {
      fist: staticFile('characters/xbot/handFist.png'),
      thumb: staticFile('characters/xbot/handThumb.png'),
      point: staticFile('characters/xbot/xbot_hand_0.png'),
      pointUp: staticFile('characters/xbot/xbot_hand_4.png'),
      open: staticFile('characters/xbot/xbot_hand_5.png'),
    },
  },
  brand: {wordmark: staticFile('brand/experimental_wordmark.png')},
  // OFFICIAL E-BOOK COVER: not supplied. Put the file in public/ebook/cover.png and set to staticFile('ebook/cover.png').
  ebookCover: null as string | null,
  music: staticFile('audio/music/perfume101_score.wav'),
  sfx: (name: string) => staticFile(`audio/sfx/${name}`),
  vo: (file: string) => staticFile(`audio/vo/${file}`),
};
// Set to true once real voice recordings exist in public/audio/vo/ (file names in config/script.ts).
export const VO_ENABLED = false;
