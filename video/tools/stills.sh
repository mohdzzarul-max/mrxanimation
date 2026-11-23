#!/bin/bash
# usage: tools/stills.sh out_prefix frame1 frame2 ... -> contact sheet out/<prefix>_sheet.jpg
P=$1; shift; mkdir -p out/stills; FILES=()
for fr in "$@"; do npx remotion still src/index.ts Perfume101 out/stills/${P}_$fr.jpg --frame $fr --scale 0.5 --image-format jpeg --props '{"audio":false}' >/dev/null 2>&1 || echo "fail $fr"; FILES+=(out/stills/${P}_$fr.jpg); done
python3 - "$P" "${FILES[@]}" <<'PY'
import sys; from PIL import Image, ImageDraw
p=sys.argv[1]; fs=sys.argv[2:]; ims=[Image.open(f) for f in fs]
w,h=ims[0].size; cols=min(4,len(ims)); rows=(len(ims)+cols-1)//cols
sheet=Image.new('RGB',(cols*w,rows*h),'white')
for i,(im,f) in enumerate(zip(ims,fs)):
    sheet.paste(im,((i%cols)*w,(i//cols)*h)); ImageDraw.Draw(sheet).text(((i%cols)*w+8,(i//cols)*h+8),f.split('_')[-1],fill=(255,0,255))
sheet.save(f'out/{p}_sheet.jpg',quality=85)
PY
