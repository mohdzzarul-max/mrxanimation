import {Config} from '@remotion/cli/config';
Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(95);
Config.setConcurrency(4);
Config.setChromiumOpenGlRenderer('swangle');
// Use a locally installed Chrome Headless Shell when present (sandboxed CI without remotion.media access).
import {existsSync} from 'fs';
const LOCAL_SHELL = '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
if (existsSync(LOCAL_SHELL)) Config.setBrowserExecutable(LOCAL_SHELL);
