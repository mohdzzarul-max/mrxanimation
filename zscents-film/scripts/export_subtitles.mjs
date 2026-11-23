// Exports out/zscents-final-chapter.ms.srt (+ .vtt) from src/config/script.json
// and the scene start times in src/config/timeline.json.
// Includes narration lines AND the on-screen title cards, with absolute times.
import fs from "node:fs";
const tl = JSON.parse(fs.readFileSync("src/config/timeline.json", "utf8"));
const sc = JSON.parse(fs.readFileSync("src/config/script.json", "utf8"));
const fps = tl.fps;
const start = Object.fromEntries(tl.scenes.map((s) => [s.id, s.from]));
const ev = tl.events;
const T = sc.titles;
const cues = sc.lines.map((l) => ({ a: (start[l.scene] + l.start) / fps, b: (start[l.scene] + l.end) / fps, t: l.text }));
const s = (id) => start[id] / fps;
cues.push(
  { a: s("s03-bilik-kayu") + 118 / fps, b: s("s03-bilik-kayu") + 300 / fps, t: `${T.rm100.value} — ${T.rm100.label}` },
  { a: s("s08-koleksi-terakhir") + 118 / fps, b: s("s08-koleksi-terakhir") + 300 / fps, t: T.finalChapter },
  { a: s("s08-koleksi-terakhir") + 160 / fps, b: s("s08-koleksi-terakhir") + 300 / fps, t: T.gratitude },
  { a: ev.tapiReveal, b: s("s09-kematian-zscents") + 414 / fps, t: T.notTheEnd },
  { a: ev.namaReveal, b: s("s09-kematian-zscents") + 414 / fps, t: T.onlyAName },
  { a: ev.permulaanReveal, b: ev.silverLight - 0.2, t: `${T.newBeginning[0]} ${T.newBeginning[1]}` },
  { a: ev.statement1, b: ev.tagline - 0.1, t: T.statements[0] },
  { a: ev.statement2, b: ev.tagline - 0.1, t: T.statements[1] },
  { a: ev.statement3, b: ev.tagline - 0.1, t: T.statements[2] },
  { a: ev.wordmarkReveal, b: ev.end, t: "EXPERIMENTAL PERFUMERY" },
  { a: ev.tagline, b: ev.end, t: T.tagline },
);
cues.sort((x, y) => x.a - y.a);
const ts = (v, sep) => {
  const ms = Math.round(v * 1000);
  const p = (n, w = 2) => String(n).padStart(w, "0");
  return `${p(Math.floor(ms / 3600000))}:${p(Math.floor(ms / 60000) % 60)}:${p(Math.floor(ms / 1000) % 60)}${sep}${p(ms % 1000, 3)}`;
};
fs.mkdirSync("out", { recursive: true });
fs.writeFileSync("out/zscents-final-chapter.ms.srt", cues.map((c, i) => `${i + 1}\n${ts(c.a, ",")} --> ${ts(c.b, ",")}\n${c.t}\n`).join("\n"));
fs.writeFileSync("out/zscents-final-chapter.ms.vtt", "WEBVTT\n\n" + cues.map((c) => `${ts(c.a, ".")} --> ${ts(c.b, ".")}\n${c.t}\n`).join("\n"));
console.log(`wrote ${cues.length} cues`);
