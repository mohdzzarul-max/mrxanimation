#!/usr/bin/env bash
# Rebuild the test: render frames -> MP4, add the music cut, make the contact sheet.
set -euo pipefail
cd "$(dirname "$0")/.."
TMP=$(mktemp -d)
node effects/render.js its-x/scientist-test --fps 24 --out "$TMP"
ffmpeg -v error -y -i "$TMP/scientist-test.mp4" -i its-x/assets/track_35.74-40.74.m4a \
  -c:v copy -c:a copy -shortest -movflags +faststart its-x/OUTPUT/ITS_X_SCIENTIST_5SEC_TEST.mp4
node its-x/stills.js
rm -rf "$TMP"
echo "done: its-x/OUTPUT/ITS_X_SCIENTIST_5SEC_TEST.mp4"
