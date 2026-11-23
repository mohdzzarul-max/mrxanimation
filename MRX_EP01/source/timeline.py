"""MR X EP01 — edit decision list (pure Python, shared by Blender shots, audio mix and compositor).

Each shot: id, scene, frames (30 fps), render range (local, inclusive start / exclusive end; frames outside
are post-only holds/black), dialogue cues [(line_id, local_frame, tempo)], sfx [(name, local_frame, gain_db)],
music state at shot start, and post fx [(kind, local_frame, params)].
"""
FPS = 30

SHOTS = []


def shot(sid, scene, frames, desc, lines=(), sfx=(), music=None, fx=(), render=None, reuse=None):
    SHOTS.append(dict(id=sid, scene=scene, frames=frames, desc=desc, lines=list(lines), sfx=list(sfx), music=music,
                      fx=list(fx), render=render or (0, frames), reuse=reuse))


# ------------------------------------------------------------------ SCENE 01 — VIRAL HOOK
shot("sh01", 1, 120, "Black, spray SFX; smash to ECU MR X eyes widen + recoil; 'WEHHH!!! AKU KENA GAME KE NI?!'; "
     "typography 80% PATI?! / OWN CREATION?!; record scratch, freeze, flashback transition",
     lines=[("s01_mrx_wehh", 14, 1.0)],
     sfx=[("spray", 0, -2), ("impact_hit", 8, -3), ("whoosh_fast", 8, -8), ("record_scratch", 92, -2)],
     music="hook",
     fx=[("black", 0, dict(until=8)), ("shake", 14, dict(amp=14, dur=14)), ("text_pop", 62, dict(t="80% PATI?!", y=0.17, col="yellow", size=118)),
         ("text_pop", 75, dict(t="OWN CREATION?!", y=0.24, col="white", size=96)), ("freeze", 92, dict(until=106)),
         ("flashback", 104, dict(until=120, t="3 HARI SEBELUM..."))],
     render=(8, 92))

# ------------------------------------------------------------------ SCENE 02 — BOOTH
shot("sh02a", 2, 66, "Tracking shot gliding past lit perfume bottles on booth shelves", music="luxury",
     sfx=[("mall_ambience", 0, -18), ("shimmer", 6, -12)], fx=[("lightsweep", 20, dict(dur=30))])
shot("sh02b", 2, 60, "Medium on UNCLE: spots MR X, waves big", lines=[("s02_unc_boss", 12, 1.0)])
shot("sh02c", 2, 60, "Wide: MR X walks into frame toward the booth", sfx=[("footsteps", 0, -10)])
shot("sh02d", 2, 78, "Over-the-shoulder from behind MR X: Uncle lifts the hero bottle",
     lines=[("s02_unc_bukan", 10, 1.0)], sfx=[("shimmer", 30, -8)])
shot("sh02e", 2, 115, "Push-in on Uncle with bottle: claims", lines=[("s02_unc_80", 8, 1.0)],
     sfx=[("promo_hit", 8, -4), ("promo_hit", 48, -4), ("promo_hit", 80, -4)],
     fx=[("claims", 8, dict(line="s02_unc_80", items=["80% PATI!", "OWN CREATION!", "BUKAN DUPE!"]))])
shot("sh02f", 2, 95, "CU MR X reaction, eyes sparkle", lines=[("s02_mrx_fuhh", 6, 1.0)],
     sfx=[("sparkle", 12, -8)], fx=[("sparkles", 10, dict(dur=80))])
shot("sh02g", 2, 105, "MCU Uncle: limited edition", lines=[("s02_unc_limited", 6, 1.0)],
     fx=[("text_pop", 40, dict(t="LIMITED EDITION!", y=0.20, col="yellow", size=80))])
shot("sh02h", 2, 60, "MR X FOMO: huge eyes, sparkles, FOMO meter",
     sfx=[("riser", 0, -8), ("sparkle", 6, -6), ("ding", 40, -6)],
     fx=[("fomo_meter", 4, dict(dur=56)), ("sparkles", 0, dict(dur=60)), ("zoom_punch", 40, dict(amt=0.06))])

# ------------------------------------------------------------------ SCENE 03 — FOMO TRAP
shot("sh03a", 3, 66, "Macro: premium packaging in MR X's hands, slow orbit, light sweep", music="luxury",
     sfx=[("shimmer", 4, -8)], fx=[("lightsweep", 18, dict(dur=34))])
shot("sh03b", 3, 92, "MR X MCU holding box, suspicious squint", lines=[("s03_mrx_betul", 6, 1.0)])
shot("sh03c", 3, 160, "Uncle: secret family formula, taps chest, glasses glint, push-in",
     lines=[("s03_unc_alaa", 6, 1.0)], sfx=[("chest_tap", 70, -6), ("glint", 100, -6)],
     fx=[("glint", 100, dict(x=0.43, y=0.40))])
shot("sh03d", 3, 30, "MR X amazed, whoosh into fantasy", sfx=[("whoosh", 18, -4), ("sparkle", 4, -8)],
     fx=[("whiteflash", 26, dict(dur=6))])
shot("sh03e", 3, 110, "FANTASY: MR X struts the runway, flashes, wind, hero pose", music="fantasy",
     sfx=[("crowd_cheer", 0, -10), ("camera_flash", 20, -10), ("camera_flash", 46, -10), ("camera_flash", 72, -8),
          ("whoosh", 78, -8)],
     fx=[("vignette_gold", 0, dict(dur=110))])
shot("sh03f", 3, 55, "SMASH back to reality: 'ON! Saya beli!' fist pump", lines=[("s03_mrx_on", 6, 1.0)], music="luxury",
     sfx=[("record_scratch_short", 0, -10), ("impact_small", 22, -6)])
shot("sh03g", 3, 45, "Two-shot: Uncle 'Ha! Bagus boss!', MR X reaches for money", lines=[("s03_unc_bagus", 4, 1.0)])

# ------------------------------------------------------------------ SCENE 04 — PURCHASE
shot("sh04a", 4, 75, "Slow-motion money handover, Uncle's eyes follow the cash", music="transaction",
     sfx=[("slowmo_whoosh", 0, -8), ("kaching", 55, -2)], fx=[("glint", 50, dict(x=0.62, y=0.30))])
shot("sh04b", 4, 72, "Uncle: 'Terbaik boss!' hands over the box", lines=[("s04_unc_terbaik", 6, 1.0)])
shot("sh04c", 4, 100, "Wide: MR X hugs box, walks away happy; Uncle waves",
     lines=[("s04_unc_terima", 40, 1.0)], sfx=[("footsteps", 10, -12)])
shot("sh04d", 4, 105, "Music drops. Uncle's smile curdles into a sly grin. Slow dolly-in. Cut to black.",
     music="suspicious", sfx=[("sting_low", 40, -6)], fx=[("black", 95, dict(until=105))], render=(0, 95))

# ------------------------------------------------------------------ SCENE 05 — DISAPPOINTMENT
shot("sh05a", 5, 75, "Bedroom: MR X at his desk sets down the box", music="curious",
     sfx=[("room_tone", 0, -20), ("box_place", 40, -6)])
shot("sh05b", 5, 90, "Unboxing macro: lid lifts, bottle comes out, cap removed",
     sfx=[("rustle", 12, -6), ("rustle", 40, -8), ("cap_click", 80, -4)])
shot("sh05c", 5, 60, "Spray on wrist PSSSHT, sniff", sfx=[("spray", 15, -2), ("sniff", 35, -4)],
     fx=[("text_pop", 16, dict(t="PSSSHT!", y=0.28, col="white", size=70))])
shot("sh05d", 5, 90, "CU: 'Eh...?' eyes narrow, sniff again and again", lines=[("s05_mrx_eh", 10, 0.6)],
     sfx=[("sniff", 40, -4), ("sniff", 65, -4)])
shot("sh05e", 5, 90, "He spots his old dupe bottle on the shelf, grabs it, sprays other wrist",
     sfx=[("glint", 12, -10), ("spray", 75, -3)])
shot("sh05f", 5, 75, "Left/right sniff comparison, cuts accelerating", music="tension",
     sfx=[("sniff", 0, -4), ("sniff", 20, -4), ("sniff", 35, -4), ("sniff", 47, -4), ("sniff", 56, -4),
          ("sniff", 63, -4), ("sniff", 69, -4)],
     fx=[("zoom_punch", 20, dict(amt=0.04)), ("zoom_punch", 35, dict(amt=0.05)), ("zoom_punch", 47, dict(amt=0.06)),
         ("zoom_punch", 56, dict(amt=0.07)), ("zoom_punch", 63, dict(amt=0.08)), ("zoom_punch", 69, dict(amt=0.09))])
shot("sh05g", 5, 80, "Realization: 'BAU NI MACAM DUPE YANG AKU DAH ADA LAH!'", lines=[("s05_mrx_bau", 6, 1.0)],
     sfx=[("orch_hit", 4, -2)], music="drama",
     fx=[("shake", 6, dict(amp=10, dur=10)), ("text_pop", 44, dict(t="BAU MACAM DUPE!", y=0.76, col="yellow", size=92))])
shot("sh05h", 5, 110, "Extreme eyes; ANGER: 'HABIS TU... KOTAK?!' red flash, speed lines, smoke, slams box",
     lines=[("s05_mrx_habis", 10, 1.0)], sfx=[("anger_rumble", 8, -6), ("steam", 40, -8), ("slam", 98, 0)],
     fx=[("anger", 8, dict(dur=95)), ("shake", 98, dict(amp=22, dur=12)), ("impact_frame", 98, dict(dur=3)),
         ("text_pop", 70, dict(t="KOTAK?!", y=0.25, col="red", size=140))])

# ------------------------------------------------------------------ SCENE 06 — THE SECRET
shot("sh06a", 6, 75, "Storeroom: door creaks open, warm light, Uncle walks in with cash", music="villain",
     sfx=[("door_creak", 3, -6), ("footsteps", 30, -12)])
shot("sh06b", 6, 88, "CU hands counting money; 'Hehehe... OWN CREATION konon!'",
     lines=[("s06_unc_hehe", 8, 1.0), ("s06_unc_konon", 44, 1.0)], sfx=[("money_count", 0, -6)])
shot("sh06c", 6, 130, "Pull back REVEAL: drums of ready-made concentrate; 'Padahal pati siap dari kilang!'",
     lines=[("s06_unc_padahal", 10, 1.0)], sfx=[("reveal_sting", 6, -4), ("drum_tap", 100, -4)],
     fx=[("label_call", 60, dict(t="READY-MADE FRAGRANCE CONCENTRATE", dur=40))])
shot("sh06d", 6, 108, "MONTAGE x6: drum / concentrate / portioning / bottle fill / packaging / finished product",
     sfx=[("whoosh_fast", 0, -10), ("whoosh_fast", 18, -10), ("pour", 36, -8), ("pour", 54, -8),
          ("whoosh_fast", 72, -10), ("shimmer", 90, -8)])
shot("sh06e", 6, 60, "Uncle holds up a pretty bottle: 'Tukar botol lawa sikit...'", lines=[("s06_unc_tukar", 6, 1.0)],
     sfx=[("shimmer", 8, -10)])
shot("sh06f", 6, 55, "Places perfume into luxury box: 'Kotak kasi premium...'", lines=[("s06_unc_kotak", 6, 1.0)],
     sfx=[("box_place", 40, -6)])
shot("sh06g", 6, 150, "'Dia ingat beli formula eksklusif!' then low-angle evil laugh, glasses flare",
     lines=[("s06_unc_ingat", 6, 1.0), ("s06_unc_haha", 86, 1.0), ("s06_unc_haha", 112, 0.9)],
     sfx=[("thunder_comic", 84, -6)],
     fx=[("darken", 84, dict(dur=66)), ("glint", 92, dict(x=0.42, y=0.36)),
         ("text_pop", 90, dict(t="OWN CREATION?", y=0.18, col="white", size=86)),
         ("text_stamp", 112, dict(t="PATI SIAP KILANG!", y=0.80, col="yellow", size=104))])

# ------------------------------------------------------------------ SCENE 07 — X-BOT
shot("sh07a", 7, 75, "MR X sits on the floor hugging the box, deflated", music="sad")
shot("sh07b", 7, 60, "BOOM! yellow shockwave; X-BOT drops in, heavy landing, rises", music="action",
     sfx=[("boom", 4, 0), ("land_thud", 25, -2)],
     fx=[("shockwave", 4, dict(col="yellow", x=0.5, y=0.45)), ("shake", 25, dict(amp=18, dur=10)),
         ("whiteflash", 4, dict(dur=4))])
shot("sh07c", 7, 50, "Low-angle hero: 'MR X!!! KAU NI MEMANG!'", lines=[("s07_xb_mrx", 4, 1.0)],
     fx=[("shake", 4, dict(amp=6, dur=8))])
shot("sh07d", 7, 60, "MR X jumps in shock: 'WOIII! KAU DATANG DARI MANA?!'", lines=[("s07_mrx_woii", 10, 1.0)],
     sfx=[("boing", 2, -6)])
shot("sh07e", 7, 62, "X-BOT points at the perfume: 'KAU BELI PERFUME KE BELI CERITA DONGENG?!'",
     lines=[("s07_xb_dongeng", 6, 1.0)], sfx=[("whoosh_fast", 4, -8)])
shot("sh07f", 7, 30, "MR X confused head tilt", sfx=[("question", 6, -8)],
     fx=[("text_pop", 6, dict(t="?", y=0.22, col="yellow", size=160))])
shot("sh07g", 7, 68, "X-BOT: 'Claim 80% pati, kau percaya!' + flashback inset", lines=[("s07_xb_claim80", 4, 1.0)],
     fx=[("inset", 8, dict(src="sh02e", src_start=10, dur=56, t="80% PATI!"))])
shot("sh07h", 7, 60, "X-BOT: 'Claim own creation, kau percaya!' + flashback inset",
     lines=[("s07_xb_claimown", 4, 1.0)], fx=[("inset", 6, dict(src="sh03c", src_start=60, dur=52, t="OWN CREATION!"))])
shot("sh07i", 7, 64, "X-BOT: 'Packaging berkilat sikit, terus checkout!' + box flashback",
     lines=[("s07_xb_packaging", 4, 1.0)], sfx=[("kaching", 46, -10)],
     fx=[("inset", 6, dict(src="sh03a", src_start=6, dur=56, t="CHECKOUT!"))])
shot("sh07j", 7, 70, "MR X looks down: 'Tapi... kotak dia cantik...'",
     lines=[("s07_mrx_tapi", 10, 0.65), ("s07_mrx_cantik", 34, 0.8)], music="sad_stop")
shot("sh07k", 7, 120, "SILENCE. X-BOT freezes, eyes narrow, slowly turns to camera. Push in. 'ASTAGAAA!'",
     lines=[("s07_xb_astaga", 100, 0.85)], music="silence", sfx=[("cricket", 20, -14), ("whoosh", 97, -6)])
shot("sh07l", 7, 65, "'KAU NAK PAKAI PERFUME KE NAK PAKAI KOTAK?!' huge shockwave + typography",
     lines=[("s07_xb_kotak", 3, 1.0)], music="action", sfx=[("boom", 3, -2), ("impact_hit", 40, -4)],
     fx=[("shockwave", 3, dict(col="yellow", x=0.5, y=0.42)), ("shake", 3, dict(amp=16, dur=14)),
         ("text_stamp", 30, dict(t="KAU NAK PAKAI KOTAK?!", y=0.78, col="yellow", size=88))])
shot("sh07m", 7, 80, "MR X topples back onto the bed; X-BOT facepalms",
     sfx=[("fall_whoosh", 4, -6), ("bed_thud", 24, -2), ("facepalm", 40, -2)],
     fx=[("shake", 24, dict(amp=8, dur=8))])

# ------------------------------------------------------------------ SCENE 08 — LESSON
shot("sh08a", 8, 85, "X-BOT calms, opens a yellow hologram: 'Guna pati siap kilang tu tak salah.'", music="lesson",
     lines=[("s08_xb_dengar", 10, 1.0)], sfx=[("holo_on", 4, -6)])
shot("sh08b", 8, 105, "Points at hologram: 'Yang salah, claim own creation kalau sebenarnya bukan!'",
     lines=[("s08_xb_salah", 6, 1.0)], sfx=[("holo_swap", 50, -8)])
shot("sh08c", 8, 100, "Faces MR X: 'Dan jangan beli sebab FOMO je! Semak dulu seller tu!'",
     lines=[("s08_xb_fomo", 6, 1.0)],
     fx=[("text_pop", 50, dict(t="SEMAK DULU SELLER!", y=0.20, col="yellow", size=80))])
shot("sh08d", 8, 80, "MR X nods sincerely: 'Faham... lepas ni aku check dulu.'",
     lines=[("s08_mrx_faham", 6, 0.7), ("s08_mrx_lepas", 34, 1.0)])

# ------------------------------------------------------------------ SCENE 09 — PUNCHLINE
shot("sh09a", 9, 75, "TING! phone lights: NEW DROP 90% PATI; MR X's eyes widen, hand creeps toward phone",
     music="punch_quiet", sfx=[("ting", 5, -2), ("sparkle", 18, -10)],
     fx=[("notif", 5, dict(dur=70))])
shot("sh09b", 9, 30, "ECU X-BOT glowing eyes: 'MR X!!!!!'", lines=[("s09_xb_mrx", 4, 1.0)],
     sfx=[("whoosh_fast", 0, -6)], fx=[("shake", 4, dict(amp=10, dur=10))])
shot("sh09c", 9, 40, "Snap zoom: MR X freezes mid-reach. FREEZE FRAME.", sfx=[("bass_drop", 8, 0)],
     fx=[("zoom_punch", 0, dict(amt=0.12)), ("freeze", 15, dict(until=40)), ("impact_frame", 8, dict(dur=2))],
     render=(0, 15))
shot("end", 9, 150, "Black. End cards + EXPERIMENTAL PERFUMERY signature", music="end",
     fx=[("endcards", 0, dict())], render=(0, 0))


def scene_starts():
    t, out = 0, {}
    for s in SHOTS:
        out[s["id"]] = t
        t += s["frames"]
    return out, t


if __name__ == "__main__":
    starts, total = scene_starts()
    for s in SHOTS:
        print(f"{s['id']:6s} S{s['scene']:02d} {starts[s['id']]:5d} +{s['frames']:4d}  {s['desc'][:70]}")
    print("TOTAL", total, "frames =", round(total / FPS, 2), "s ;  rendered frames:",
          sum(s['render'][1] - s['render'][0] for s in SHOTS))
