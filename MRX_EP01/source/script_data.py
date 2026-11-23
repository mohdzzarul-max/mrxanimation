"""MR X — EP01: KENA GAME!  Dialogue source of truth.

Each line: id, speaker, subtitle text (exact, shown on screen), tts text
(phonetic spelling for the MMS Malay model: lowercase, no v/x, numbers spelled).
Speakers: MRX, UNCLE, XBOT.
"""

LINES = [
    # SCENE 01 — hook
    ("s01_mrx_wehh", "MRX", "WEHHH!!! AKU KENA GAME KE NI?!", "wehhh! aku kena gem ke ni?"),
    # SCENE 02 — booth
    ("s02_unc_boss", "UNCLE", "Boss! Boss! Mari sini!", "bos! bos! mari sini!"),
    ("s02_unc_bukan", "UNCLE", "Ni bukan perfume biasa-biasa tau!", "ni bukan perfum biasa-biasa tau!"),
    ("s02_unc_80", "UNCLE", "80% PATI! OWN CREATION! BUKAN DUPE!",
     "lapan puluh peratus pati! oun kriesyen! bukan diup!"),
    ("s02_mrx_fuhh", "MRX", "Fuhhh! 80% pati?! Own creation pulak tu?!",
     "fuhhh! lapan puluh peratus pati? oun kriesyen pulak tu?"),
    ("s02_unc_limited", "UNCLE", "Ha'ah boss! Limited edition! Formula eksklusif!",
     "ha'ah bos! limited edisyen! formula eksklusif!"),
    # SCENE 03 — FOMO trap
    ("s03_mrx_betul", "MRX", "Betul ke uncle? Ni bukan inspired perfume lain?",
     "betul ke angkel? ni bukan inspaiyed perfum lain?"),
    ("s03_unc_alaa", "UNCLE", "Alaaa boss! Uncle sendiri cipta formula ni. Rahsia tujuh keturunan!",
     "alaaa bos! angkel sendiri cipta formula ni. rahsia tujuh keturunan!"),
    ("s03_mrx_on", "MRX", "Fuhhh! ON! Saya beli!", "fuhhh! on! saya beli!"),
    ("s03_unc_bagus", "UNCLE", "Ha! Bagus boss!", "ha! bagus bos!"),
    # SCENE 04 — purchase
    ("s04_unc_terbaik", "UNCLE", "Terbaik boss! Memang pilihan bijak!", "terbaik bos! memang pilihan bijak!"),
    ("s04_unc_terima", "UNCLE", "Terima kasih boss! Datang lagi!", "terima kasih bos! datang lagi!"),
    # SCENE 05 — disappointment
    ("s05_mrx_eh", "MRX", "Eh...?", "ehhh?"),
    ("s05_mrx_bau", "MRX", "WEHHH! BAU NI MACAM DUPE YANG AKU DAH ADA LAH!",
     "wehhh! bau ni macam diup yang aku dah ada lah!"),
    ("s05_mrx_habis", "MRX", "HABIS TU AKU BAYAR MAHAL UNTUK APA?! KOTAK?!",
     "habis tu aku bayar mahal untuk apa? kotak?"),
    # SCENE 06 — the secret
    ("s06_unc_hehe", "UNCLE", "Hehehehe...", "he he he he he"),
    ("s06_unc_konon", "UNCLE", "OWN CREATION konon!", "oun kriesyen konon!"),
    ("s06_unc_padahal", "UNCLE", "Padahal pati siap dari kilang! Aku beli bertong-tong je! HAHAHA!",
     "padahal pati siap dari kilang! aku beli bertong-tong je! hahaha!"),
    ("s06_unc_tukar", "UNCLE", "Tukar botol lawa sikit...", "tukar botol lawa sikit..."),
    ("s06_unc_kotak", "UNCLE", "Kotak kasi premium...", "kotak kasi premium..."),
    ("s06_unc_ingat", "UNCLE", "Dia ingat beli formula eksklusif!", "dia ingat beli formula eksklusif!"),
    ("s06_unc_haha", "UNCLE", "HAHAHAHA!", "ha ha ha ha ha ha ha ha!"),
    # SCENE 07 — X-BOT
    ("s07_xb_mrx", "XBOT", "MR X!!! KAU NI MEMANG!", "mister eks! kau ni memang!"),
    ("s07_mrx_woii", "MRX", "WOIII! KAU DATANG DARI MANA?!", "woiii! kau datang dari mana?"),
    ("s07_xb_dongeng", "XBOT", "KAU BELI PERFUME KE BELI CERITA DONGENG?!",
     "kau beli perfum ke beli cerita dongeng?"),
    ("s07_xb_claim80", "XBOT", "Claim 80% pati, kau percaya!", "klem lapan puluh peratus pati, kau percaya!"),
    ("s07_xb_claimown", "XBOT", "Claim own creation, kau percaya!", "klem oun kriesyen, kau percaya!"),
    ("s07_xb_packaging", "XBOT", "Packaging berkilat sikit, terus checkout!",
     "pekejing berkilat sikit, terus cekaut!"),
    ("s07_mrx_tapi", "MRX", "Tapi...", "tapi..."),
    ("s07_mrx_cantik", "MRX", "kotak dia cantik...", "kotak dia cantik..."),
    ("s07_xb_astaga", "XBOT", "ASTAGAAA!", "astagaaaaa!"),
    ("s07_xb_kotak", "XBOT", "KAU NAK PAKAI PERFUME KE NAK PAKAI KOTAK?!",
     "kau nak pakai perfum ke nak pakai kotak?"),
    # SCENE 08 — lesson
    ("s08_xb_dengar", "XBOT", "Dengar sini. Guna pati siap kilang tu tak salah.",
     "dengar sini. guna pati siap kilang tu tak salah."),
    ("s08_xb_salah", "XBOT", "Yang salah, claim own creation kalau sebenarnya bukan!",
     "yang salah, klem oun kriesyen kalau sebenarnya bukan!"),
    ("s08_xb_fomo", "XBOT", "Dan jangan beli sebab FOMO je! Semak dulu seller tu!",
     "dan jangan beli sebab fomo je! semak dulu seler tu!"),
    ("s08_mrx_faham", "MRX", "Faham...", "faham..."),
    ("s08_mrx_lepas", "MRX", "lepas ni aku check dulu.", "lepas ni aku cek dulu."),
    # SCENE 09 — punchline
    ("s09_xb_mrx", "XBOT", "MR X!!!!!", "misterrr ekssss!"),
]

LINE = {l[0]: dict(id=l[0], who=l[1], sub=l[2], tts=l[3]) for l in LINES}

# Voice design (applied in audio/tts.py). MMS gives one base voice; identity is
# built from pitch, formant, pace, seed and character-specific processing.
VOICES = {
    "MRX":   dict(seed=11, speaking_rate=1.08, noise_scale=0.75, pitch=+2.0, formant=True),
    "UNCLE": dict(seed=3,  speaking_rate=0.94, noise_scale=0.70, pitch=-3.5, formant=True),
    "XBOT":  dict(seed=7,  speaking_rate=1.15, noise_scale=0.80, pitch=+3.0, formant=False, robot=True),
}
