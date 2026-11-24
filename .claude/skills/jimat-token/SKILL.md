---
name: jimat-token
description: Save tokens. Rewrite a long prompt into a short, precise one, and work in low-token mode (short replies, no re-reading, targeted reads). Use when the user says "pendekkan prompt", "jimat token", "save tokens", "shorten my prompt", or pastes a long prompt to compress.
---

# Jimat token

## A. Shorten a prompt (when the user gives one)
Return ONLY the compressed prompt in a code block, then one line: `~X -> ~Y words`.
Rules:
1. Keep: goal, hard constraints, output format, names/numbers/paths, examples that define the style.
2. Cut: greetings, politeness, repeated ideas, "please make sure", explanations of why, filler adjectives.
3. Use the shape: `Goal: ... | Input: ... | Constraints: a; b; c | Output: ...`
4. Lists over sentences. Numbers over words. One idea per line.
5. Never drop a requirement. If two lines conflict, ask once.
6. Keep the user's language (Malay/English) unless asked.

Example - in: "Boleh tak awak tolong buatkan satu animation pendek dalam 10 saat, gaya kartun tahun 2000an, ada hero hantu yang bertukar bentuk, dan tolong render jadi mp4 vertical untuk TikTok ya, terima kasih"
out: `Animasi 10s, gaya kartun TV 2000an. Hero hantu bertukar bentuk. Output: MP4 9:16 (TikTok).`

## B. Low-token working mode (for the rest of the session)
- Replies: answer first, max ~5 lines unless asked. No recap of what the user said.
- Read only the lines needed (`sed -n`, `grep -n`), never whole big files twice.
- Don't re-run tools to "verify" what a tool already confirmed.
- Batch independent tool calls in one turn.
- Prefer editing over rewriting files.
- Suggest `/compact` when the conversation gets long, and `/clear` between unrelated tasks.
