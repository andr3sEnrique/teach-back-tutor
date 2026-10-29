#!/usr/bin/env python3
"""Build a self-contained HTML lesson page with narrated audio and a synced transcript.

Usage:
    python3 build_lesson.py lesson.json [-o lesson.html]

lesson.json:
{
  "title": "Session 1 · Fundamentals",
  "subtitle": "Click any sentence to jump there.",          (optional)
  "tracks": [                                                 (1 or more; one tab each)
    {"id": "es", "label": "Español", "lang": "es",
     "voice": "Mónica",                                       (optional, macOS voice name)
     "text": "Paragraph one. Uses {key term} markup.\n\nParagraph two."}
  ],
  "figures": [{"caption": "How X works", "svg": "<svg ...>...</svg>"}],   (optional)
  "glossary": [{"term": "key term", "def": "What it means."}]           (optional)
}

Paragraphs are separated by blank lines. Wrap key terms in {braces}: they are
highlighted on the page and read normally by the voice.

Audio uses macOS `say` or `espeak-ng` when present. Without either, the page is
built with the transcript only, so the lesson still works.
"""
import argparse
import base64
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import wave

RATE = 22050
SENTENCE_GAP = 0.25
PARAGRAPH_GAP = 0.6
# macOS novelty voices that sound bad for teaching
NOVELTY = {"Albert", "Bad News", "Bahh", "Bells", "Boing", "Bubbles", "Cellos", "Good News",
           "Jester", "Organ", "Superstar", "Trinoids", "Whisper", "Wobble", "Zarvox", "Junior",
           "Fred", "Kathy", "Ralph"}


def split_sentences(paragraph):
    parts = re.split(r"(?<=[.!?…:。！？])\s+", paragraph.strip())
    return [p for p in parts if p.strip()]


def pick_say_voice(lang):
    try:
        out = subprocess.run(["say", "-v", "?"], capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    prefix = lang.lower().replace("-", "_")
    for line in out.splitlines():
        m = re.match(r"^(.+?)\s+([a-z]{2,3}_[A-Z0-9]+)\s+#", line)
        if not m:
            continue
        name, locale = m.group(1).strip(), m.group(2)
        base = name.split(" (")[0]
        if base in NOVELTY:
            continue
        if locale.lower() == prefix or locale.lower().startswith(prefix.split("_")[0] + "_"):
            return name
    return None


def tts_engine():
    if shutil.which("say"):
        return "say"
    if shutil.which("espeak-ng"):
        return "espeak-ng"
    return None


def synth(engine, text, lang, voice, path):
    if engine == "say":
        cmd = ["say", "--file-format=WAVE", f"--data-format=LEI16@{RATE}", "-o", path]
        if voice:
            cmd += ["-v", voice]
        subprocess.run(cmd + [text], check=True)
    else:
        subprocess.run(["espeak-ng", "-v", voice or lang, "-w", path, text], check=True)


def read_frames(path):
    with wave.open(path, "rb") as w:
        if w.getnchannels() != 1 or w.getsampwidth() != 2:
            raise RuntimeError(f"unexpected audio format in {path}")
        return w.getframerate(), w.readframes(w.getnframes())


def silence(rate, seconds):
    return b"\x00\x00" * int(rate * seconds)


def build_track(track, engine, tmp):
    paragraphs = [p for p in re.split(r"\n\s*\n", track["text"].strip()) if p.strip()]
    segments = []
    for pi, para in enumerate(paragraphs):
        for s in split_sentences(para):
            segments.append({"p": pi, "raw": s})

    def to_html(s):
        return re.sub(r"\{(.+?)\}", r"<mark>\1</mark>", html.escape(s, quote=False))

    if not engine:
        return None, [{"p": s["p"], "t": None, "h": to_html(s["raw"])} for s in segments]

    lang = track.get("lang", "en")
    voice = track.get("voice") or (pick_say_voice(lang) if engine == "say" else None)
    if engine == "say" and not voice:
        print(f"warning: no macOS voice for '{lang}', using the system default", file=sys.stderr)

    pcm, rate, t, out = [], None, 0.0, []
    prev_p = None
    for i, s in enumerate(segments):
        spoken = re.sub(r"[{}]", "", s["raw"])
        path = os.path.join(tmp, f"{track['id']}-{i}.wav")
        synth(engine, spoken, lang, voice, path)
        r, frames = read_frames(path)
        if rate is None:
            rate = r
        elif r != rate:
            raise RuntimeError("TTS returned mixed sample rates")
        if prev_p is not None:
            gap = PARAGRAPH_GAP if s["p"] != prev_p else SENTENCE_GAP
            pcm.append(silence(rate, gap))
            t += gap
        out.append({"p": s["p"], "t": round(t, 2), "h": to_html(s["raw"])})
        pcm.append(frames)
        t += len(frames) / 2 / rate
        prev_p = s["p"]

    wav_path = os.path.join(tmp, f"{track['id']}.wav")
    with wave.open(wav_path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"".join(pcm))
    return compress(wav_path), out


def compress(wav_path):
    """Return a data URI, AAC when a converter is available, WAV otherwise."""
    m4a = wav_path[:-4] + ".m4a"
    try:
        if shutil.which("afconvert"):
            subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", "-b", "48000", wav_path, m4a],
                           check=True, capture_output=True)
        elif shutil.which("ffmpeg"):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav_path,
                            "-c:a", "aac", "-b:a", "48k", m4a], check=True)
        else:
            raise FileNotFoundError
        path, mime = m4a, "audio/mp4"
    except (OSError, subprocess.CalledProcessError):
        path, mime = wav_path, "audio/wav"
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


PAGE = """<!doctype html><html lang="__LANG__"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>__TITLE__</title>
<style>
:root{--bg:#faf9f5;--card:#fff;--tx:#1f1e1d;--mut:#6b6a66;--bd:#e5e3dc;--hl:#e6f1fb;--hlt:#0c447c;--mk:#faeeda;--mkt:#633806;--ac:#185fa5}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#1f1e1d;--card:#2a2927;--tx:#ecebe6;--mut:#a3a19a;--bd:#3d3c39;--hl:#0c447c;--hlt:#e6f1fb;--mk:#633806;--mkt:#faeeda;--ac:#85b7eb}}
:root[data-theme="dark"]{--bg:#1f1e1d;--card:#2a2927;--tx:#ecebe6;--mut:#a3a19a;--bd:#3d3c39;--hl:#0c447c;--hlt:#e6f1fb;--mk:#633806;--mkt:#faeeda;--ac:#85b7eb}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--tx);font:16px/1.7 -apple-system,system-ui,sans-serif}
main{max-width:760px;margin:0 auto;padding:24px 16px 64px}
h1{font-size:22px;font-weight:600;margin:0 0 4px}h2{font-size:17px;font-weight:600;margin:32px 0 8px}
.sub{color:var(--mut);font-size:14px;margin:0 0 20px}
.bar{position:sticky;top:0;background:var(--bg);padding:12px 0;border-bottom:1px solid var(--bd);z-index:2}
.tabs{display:flex;gap:8px;margin-bottom:10px;flex-wrap:wrap}
button{font:inherit;font-size:14px;padding:5px 12px;border:1px solid var(--bd);background:var(--card);color:var(--tx);border-radius:8px;cursor:pointer}
button.on{border-color:var(--ac);color:var(--ac)}
audio{width:100%}.tr p{margin:0 0 14px}
.s{border-radius:4px;padding:1px 2px;transition:background .2s}.has-audio .s{cursor:pointer}.has-audio .s:hover{background:var(--bd)}
.s.cur{background:var(--hl);color:var(--hlt)}
mark{background:var(--mk);color:var(--mkt);border-radius:3px;padding:0 3px}
figure{margin:20px 0;padding:16px;background:var(--card);border:1px solid var(--bd);border-radius:12px}
figure svg,figure img{max-width:100%;height:auto;display:block;margin:0 auto}
figcaption{font-size:13px;color:var(--mut);margin-top:8px;text-align:center}
dl{display:grid;grid-template-columns:minmax(0,200px) minmax(0,1fr);gap:6px 16px;margin:0}
dt{font-weight:600}dd{margin:0;color:var(--mut)}
@media (max-width:520px){dl{grid-template-columns:1fr}dd{margin-bottom:8px}}
</style></head><body><main>
<h1>__TITLE__</h1>__SUB__
<div class="bar"><div class="tabs">__TABS__<span style="flex:1"></span>__SPEED__</div>__AUDIO__</div>
__FIGURES__
<div class="tr" id="tr"></div>
__GLOSSARY__
</main><script>
const T=__DATA__;
const a=document.getElementById('a'),tr=document.getElementById('tr');let cur=[],rate=1,last=null;
function load(l){if(a){a.src=T[l].src||'';a.playbackRate=rate}tr.innerHTML='';cur=[];let p=-1,el;
 tr.classList.toggle('has-audio',!!T[l].src);
 T[l].d.forEach(s=>{if(s.p!==p){el=document.createElement('p');tr.appendChild(el);p=s.p}
  const sp=document.createElement('span');sp.className='s';sp.innerHTML=s.h+' ';
  if(T[l].src&&s.t!==null){sp.onclick=()=>{a.currentTime=s.t+0.01;a.play()};cur.push([s.t,sp])}el.appendChild(sp)});
 document.querySelectorAll('[data-l]').forEach(b=>b.classList.toggle('on',b.dataset.l===l))}
if(a){a.ontimeupdate=()=>{let x=null;for(const c of cur)if(a.currentTime>=c[0])x=c[1];
 if(x!==last){last&&last.classList.remove('cur');x&&x.classList.add('cur');x&&x.scrollIntoView({block:'center',behavior:'smooth'});last=x}};
 a.onloadedmetadata=()=>{a.playbackRate=rate}}
document.querySelectorAll('[data-l]').forEach(b=>b.onclick=()=>load(b.dataset.l));
document.querySelectorAll('[data-r]').forEach(b=>b.onclick=()=>{rate=+b.dataset.r;if(a)a.playbackRate=rate;document.querySelectorAll('[data-r]').forEach(x=>x.classList.toggle('on',x===b))});
load(Object.keys(T)[0]);
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", help="lesson JSON file")
    ap.add_argument("-o", "--output", help="output HTML (default: next to the JSON)")
    ap.add_argument("--no-audio", action="store_true", help="skip speech synthesis")
    args = ap.parse_args()

    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)
    tracks = spec.get("tracks") or []
    if not tracks:
        sys.exit("lesson JSON needs at least one track")

    engine = None if args.no_audio else tts_engine()
    if not engine and not args.no_audio:
        print("warning: no TTS engine found (say / espeak-ng); building transcript-only page", file=sys.stderr)

    data = {}
    with tempfile.TemporaryDirectory() as tmp:
        for tr in tracks:
            src, segs = build_track(tr, engine, tmp)
            data[tr["id"]] = {"src": src, "d": segs}

    esc = lambda s: html.escape(s or "", quote=True)
    tabs = "".join(f'<button data-l="{esc(t["id"])}">{esc(t.get("label", t["id"]))}</button>'
                   for t in tracks) if len(tracks) > 1 else ""
    has_audio = any(v["src"] for v in data.values())
    speed = "".join(f'<button data-r="{r}"{" class=on" if r == "1" else ""}>{r}×</button>'
                    for r in ("0.8", "1", "1.2", "1.5")) if has_audio else ""
    figures = "".join(f'<figure>{fig.get("svg", "")}<figcaption>{esc(fig.get("caption"))}</figcaption></figure>'
                      for fig in spec.get("figures", []))
    gloss = spec.get("glossary") or []
    glossary = ("<h2>" + esc(spec.get("glossary_title", "Glossary")) + "</h2><dl>" +
                "".join(f'<dt><mark>{esc(g["term"])}</mark></dt><dd>{esc(g["def"])}</dd>' for g in gloss) +
                "</dl>") if gloss else ""
    sub = f'<p class="sub">{esc(spec["subtitle"])}</p>' if spec.get("subtitle") else ""

    page = (PAGE.replace("__LANG__", esc(tracks[0].get("lang", "en")))
            .replace("__TITLE__", esc(spec.get("title", "Lesson")))
            .replace("__SUB__", sub).replace("__TABS__", tabs).replace("__SPEED__", speed)
            .replace("__AUDIO__", '<audio id="a" controls preload="auto"></audio>' if has_audio else "")
            .replace("__FIGURES__", figures).replace("__GLOSSARY__", glossary)
            .replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")))

    out = args.output or os.path.splitext(args.spec)[0] + ".html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"wrote {out} ({os.path.getsize(out) // 1024} KB, audio: {'yes' if has_audio else 'no'})")


if __name__ == "__main__":
    main()
