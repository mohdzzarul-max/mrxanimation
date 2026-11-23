"""Generate SRT subtitles + VO recording script from src/config/script.ts (single source of truth)."""
import re
src=open('src/config/script.ts').read()
L=re.findall(r"\{id: '(\w+)', speaker: '(\w+)', from: (\d+), to: (\d+), text: '((?:[^'\\]|\\.)*)', vo: '([^']+)'\}",src)
FPS=30
def tc(fr):
    ms=round(fr/FPS*1000); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'
def tcs(fr): s=fr/FPS; return f'00:{int(s//60):02}:{s%60:05.2f}'
NAME={'MRX':'MR X','XBOT':'X-BOT'}
with open('deliverables/Perfume101_subtitles.srt','w') as f:
    for i,(id_,sp,a,b,t,vo) in enumerate(L,1):
        f.write(f'{i}\n{tc(int(a))} --> {tc(int(b))}\n{t}\n\n')
with open('deliverables/DIALOGUE_SCRIPT.md','w') as f:
    f.write('# PERFUME 101 — "PERFUME MAHAL MESTI TAHAN LAMA?!"\n## Dialogue & voice-over recording script (60 s, 30 fps)\n\n')
    f.write('Voices: **MR X** — natural Malaysian male, casual, confident, slightly sarcastic. **X-BOT** — energetic, cheeky, slightly stylised (light pitch-up / bit-crush in post is fine).\n\n')
    f.write('Each take must fit inside its window (start→end). Record 48 kHz WAV, mono or stereo, ~0.2 s room tone at head. Save as the file name shown into `video/public/audio/vo/`, then set `VO_ENABLED = true` in `video/src/config/assets.ts` and re-render. Music auto-ducks under dialogue.\n\n')
    f.write('| # | Speaker | Start | End | Window | Line (Bahasa Melayu) | File | Direction |\n|---|---|---|---|---|---|---|---|\n')
    DIR={'L1':'Shocked, rising disbelief; punch "lapan ratus" and "gila".','L2':'Quick, cheeky interruption.','L3':'Confident myth-buster, stress "bukan jaminan".','L4':'Penny-drops "Ohh", then list the four factors clearly.','L5':'Friendly warning, slightly faster; stress "claim seller".','L6':'Warm, persuasive, a little proud.','L7':'Upbeat sales hit; land "RM10.90 je!" then the slogan.'}
    for id_,sp,a,b,t,vo in L:
        a,b=int(a),int(b)
        f.write(f'| {id_} | {NAME[sp]} | {tcs(a)} | {tcs(b)} | {(b-a)/FPS:.1f} s | {t} | `{vo}` | {DIR.get(id_,"")} |\n')
    f.write('\n### Scene map\n| Time | Scene | What happens |\n|---|---|---|\n')
    for row in [('00:00–00:06','01 Hook','Bottle slam, RM800 tag, panel tear, Mr X shock, headline, record scratch + dramatic pause, X-BOT peeks.'),
                ('00:06–00:15','02 Myth','X-BOT jumps in, finger wag, MAHAL vs MURAH split-screen with unknown-longevity meters, "HARGA ≠ KETAHANAN".'),
                ('00:15–00:27','03 Factors','Four-panel wall: formula, ingredients, skin, weather & application; X-BOT points, Mr X hops between panels.'),
                ('00:27–00:40','04 Claims','Claims board drops, four seller claims marker-circled with gags, "CHECK DULU!" stamp.'),
                ('00:40–00:50','05 E-book','Comic panel unfolds into the e-book, four benefits, Mr X presents.'),
                ('00:50–01:00','06 CTA','RM800 struck out, RM10.90 slam, DM CTA, brand lock-up, slogan; final info held ≥ 3 s.')]:
        f.write(f'| {row[0]} | {row[1]} | {row[2]} |\n')
print(len(L),'lines')
