#!/bin/bash
# Encode composited frames + final mix into the delivery MP4 (1080x1920, 30 fps, H.264 + AAC).
# Usage: assemble.sh [out.mp4] [start_frame] [num_frames]   (defaults: full film)
set -e
cd "$(dirname "$0")/../.."
OUT=${1:-exports/MRX_EP01_KENA_GAME.mp4}
START=${2:-0}
N=${3:-}
SS=$(python3 -c "print($START/30)")
LIM=""; [ -n "$N" ] && LIM="-frames:v $N"
AT=""; [ -n "$N" ] && AT="-t $(python3 -c "print($N/30)")"
ffmpeg -v error -y -framerate 30 -start_number $START -i renders/_comp/%05d.jpg \
  -ss $SS $AT -i audio/final_mix.wav \
  $LIM -c:v libx264 -preset slow -crf 18 -profile:v high -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest "$OUT"
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate -of compact "$OUT"
