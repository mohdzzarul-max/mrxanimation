import {loadFont} from '@remotion/fonts';
import {staticFile} from 'remotion';

// Fonts are bundled locally (SIL Open Font License) so renders never depend on network access.
let loaded = false;
export const loadAllFonts = () => {
  if (loaded) return;
  loaded = true;
  loadFont({family: 'Montserrat', url: staticFile('fonts/Montserrat-Variable.woff2'), weight: '100 900'});
  loadFont({family: 'Bangers', url: staticFile('fonts/Bangers.woff2')});
  loadFont({family: 'Permanent Marker', url: staticFile('fonts/PermanentMarker.woff2')});
};
