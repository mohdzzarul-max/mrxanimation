# MR X video effects

20 reusable video effects. Each is one HTML file whose state is a pure function of time
(`window.seek(t)`), so it renders frame-accurately to video. Default canvas is 1080×1920 at 30 fps,
with a 6% side margin and the bottom 15% kept clear for captions.

`showreel.mp4` plays all 20 in a row.

## Render

```bash
node effects/render.js                                  # every effect → effects/renders/<name>.mp4
node effects/render.js orbit snap-zoom                  # only these
node effects/render.js orbit --footage me.mp4           # your clip instead of the placeholder speaker
node effects/render.js b-roll-overlay --footage me.mp4 --broll city.mp4
node effects/render.js checklist-pop --alpha            # transparent overlay → .webm (VP9 alpha)
```

Needs Node 18+, ffmpeg, and Playwright (`npm i -D playwright && npx playwright install chromium`).
To preview one in a browser, open the HTML file; it loops. Add `?t=1.5` to hold one frame.

## Effects

| File | What it does | Inputs |
|---|---|---|
| `orbit` | Labels circle the speaker's head; the far half passes behind them | footage |
| `chat-takeover` | Shot pushes back and blurs, a chat window fills the frame, messages pop in | footage |
| `frame-escape` | Shot shrinks into a card while the speaker climbs out over its top edge | footage |
| `snap-zoom` | Two fast punch-ins on the face with a spring settle and a flash | footage |
| `checklist-pop` | Card over the shot; items pop in and tick with a spark burst | footage |
| `checklist` | Full-screen tally: ticks, rolling counter, progress bar, ALL DONE stamp | — |
| `headline-storm` | Headlines fly in from every side and pile up; a final one slams on top | — |
| `zoom-portal` | A glowing portal opens in shot A; the camera flies through into shot B | footage, broll |
| `growth-curve` | Line chart draws itself, value tag rides the tip, headline counts up | — |
| `studio-reveal` | Lights flicker on, spot beams swing onto the speaker, title rises | footage |
| `b-roll-overlay` | Rounded inset clip drops in over the shot, plays, slides out | footage, broll |
| `paper-cutout` | Stop-motion torn paper layers, speaker cutout, ransom-note title | footage |
| `dolly-zoom` | Vertigo: real 3D corridor stretches while the speaker stays the same size | footage |
| `magazine-cover` | Masthead behind the head, cover lines, then pulls back to a printed cover | footage |
| `liquid-glass` | Frosted glass notification, side bar and player float over the shot | footage |
| `zoom-through-cut` | Zoom accelerates into the cut and decelerates out, with zoom blur | footage, broll |
| `green-screen` | Real per-pixel chroma key, before/after wipe onto a new background | footage (green-screen clip), broll |
| `frame-break` | A play button smashes through a picture frame's corner; shards fall | broll |
| `digital-zoom` | Pixelated crop zoom that "enhances" to sharp, under a camcorder HUD | footage |
| `phone-mockup` | Phone swings up in 3D, the app feed scrolls, a tap lands on a card | footage |

Without `--footage` / `--broll`, a placeholder speaker silhouette and a dusk-skyline clip stand in.
Real footage has no cutout, so effects that put things *behind* the speaker (`orbit`, `frame-escape`,
`magazine-cover`, `studio-reveal`, `dolly-zoom`) fall back to drawing over the whole shot.

## Editing

- Text, colours and timing sit in constants at the top of each file's script.
- Brand colours and fonts are CSS variables in `lib/fx.css` (`--accent`, `--bg`, `--sans`, …).
- `lib/fx.js` holds the shared helpers: easing (`out`, `back`, `spring`, …), the seeded random,
  footage loading and the placeholder speaker.
