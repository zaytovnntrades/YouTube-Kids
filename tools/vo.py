#!/usr/bin/env python3
"""Free, offline voiceovers for Little Ninja Safety Academy (Piper TTS + FFmpeg).

  python tools/vo.py setup                      # one-time: download the free voice models
  python tools/vo.py audition kiko [--count 12] # same line in many voices, so you can pick one
  python tools/vo.py line kiko "Ninja eyes ON!" # render one line
  python tools/vo.py script scripts/001-x.md    # render every VO line in a script

Script lines are read from lines shaped like:   KIKO: "Ninja eyes ON!"
(also SENSEI HOOT:, ZIP:, NARRATOR:, with or without a leading "VO" / "SOUND / VO:").
Output: audio/vo/<id>/NN-<character>.wav plus audio/vo/<id>-vo.wav (all lines,
0.4s gaps, loudness-normalized to -14 LUFS like the Shorts in CLAUDE.md section 5).

Nothing leaves your machine and nothing costs credits. These are still synthetic
voices, though, so CLAUDE.md section 7.8 applies: turn on the AI / synthetic labels.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VOICES = ROOT / "tools" / "voices"
CAST = json.loads((ROOT / "tools" / "cast_voices.json").read_text())
OUT = ROOT / "audio" / "vo"
GAP_S = 0.4

ALIASES = {"hoot": "sensei hoot", "sensei": "sensei hoot"}
LINE_RE = re.compile(
    r"^\s*(?:[-*]\s*)?(?:(?:SOUND\s*/\s*)?VO\s*[:\-]\s*)?"
    r"(KIKO|SENSEI HOOT|HOOT|SENSEI|ZIP|NARRATOR)\s*(?:\([^)]*\))?\s*:\s*[\"“]?(.+?)[\"”]?\s*$",
    re.IGNORECASE,
)


def rel(p):
    p = Path(p).resolve()
    return p.relative_to(ROOT) if p.is_relative_to(ROOT) else p


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        sys.exit(f"Command failed: {' '.join(map(str, cmd[:3]))} ...\n{r.stderr[-800:]}")
    return r


def character(name):
    key = ALIASES.get(name.lower(), name.lower())
    if key not in CAST:
        sys.exit(f"Unknown character '{name}'. Known: {', '.join(k for k in CAST if not k.startswith('_'))}")
    return key, CAST[key]


def model_path(cfg):
    p = VOICES / f"{cfg['model']}.onnx"
    if not p.exists():
        sys.exit(f"Missing voice model {p.name}. Run: python tools/vo.py setup")
    return p


def fx_filter(pitch, tempo):
    """Pitch shift by semitones without changing speed, then apply tempo."""
    f = 2 ** (pitch / 12.0)
    chain = []
    if abs(pitch) > 1e-6:
        chain += [f"asetrate=22050*{f:.6f}", "aresample=22050"]
    t = tempo / f
    while t > 2.0:  # atempo accepts 0.5–2.0 per stage
        chain.append("atempo=2.0"); t /= 2.0
    while t < 0.5:
        chain.append("atempo=0.5"); t /= 0.5
    chain.append(f"atempo={t:.6f}")
    return ",".join(chain)


def render(text, cfg, out, speaker=None):
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        raw = Path(td) / "raw.wav"
        txt = Path(td) / "in.txt"
        txt.write_text(text)
        run([sys.executable, "-m", "piper", "-m", str(model_path(cfg)), "-i", str(txt), "-f", str(raw),
             "-s", str(cfg["speaker"] if speaker is None else speaker),
             "--length-scale", str(cfg.get("length_scale", 1.0))])
        # Resample to Piper's 22050 Hz first so the pitch math is exact for any model.
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af",
             "aresample=22050," + fx_filter(cfg.get("pitch", 0), cfg.get("tempo", 1.0)),
             "-ar", "48000", "-ac", "1", str(out)])
    return out


def cmd_setup(_):
    VOICES.mkdir(parents=True, exist_ok=True)
    models = sorted({c["model"] for k, c in CAST.items() if not k.startswith("_")})
    run([sys.executable, "-m", "piper.download_voices", "--download-dir", str(VOICES), *models])
    print("Downloaded:", ", ".join(models))
    print("License check: read each voice's MODEL_CARD on huggingface.co/rhasspy/piper-voices "
          "before monetized use (see tools/VOICEOVER.md).")


def cmd_audition(a):
    key, cfg = character(a.character)
    start = a.start
    outdir = ROOT / "audio" / "auditions" / key.replace(" ", "-")
    for s in range(start, start + a.count):
        render(a.text or cfg["test_line"], cfg, outdir / f"speaker-{s:03d}.wav", speaker=s)
    print(f"Rendered {a.count} takes to {rel(outdir)}/. Put your favourite id in "
          f"tools/cast_voices.json -> \"{key}\".speaker")


def cmd_line(a):
    key, cfg = character(a.character)
    out = Path(a.out) if a.out else OUT / "lines" / f"{key.replace(' ', '-')}.wav"
    print(rel(render(a.text, cfg, out)))


def parse_script(path):
    lines = []
    for raw in Path(path).read_text().splitlines():
        m = LINE_RE.match(raw)
        if m:
            text = m.group(2).strip().strip('"“”')
            if text:
                lines.append((character(m.group(1))[0], text))
    return lines


def cmd_script(a):
    path = Path(a.path)
    lines = parse_script(path)
    if not lines:
        sys.exit(f'No VO lines found in {path}. Format them like:  KIKO: "Ninja eyes ON!"')
    sid = path.stem.split("-")[0]
    outdir = OUT / sid
    parts = []
    for i, (key, text) in enumerate(lines, 1):
        p = render(text, CAST[key], outdir / f"{i:02d}-{key.replace(' ', '-')}.wav")
        parts.append(p)
        print(f"{i:02d} {key:12s} {text}")
    with tempfile.TemporaryDirectory() as td:
        silence = Path(td) / "gap.wav"
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
             f"anullsrc=r=48000:cl=mono", "-t", str(GAP_S), str(silence)])
        lst = Path(td) / "list.txt"
        seq = []
        for p in parts:
            seq += [p, silence]
        lst.write_text("".join(f"file '{p}'\n" for p in seq[:-1]))
        final = OUT / f"{sid}-vo.wav"
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
             "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", str(final)])
    dur = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(final)]).stdout.strip()
    words = sum(len(t.split()) for _, t in lines)
    print(f"\n{rel(final)}  {float(dur):.1f}s  {words} words "
          f"({words / float(dur):.1f} words/s; target is about 2)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup").set_defaults(fn=cmd_setup)
    p = sub.add_parser("audition"); p.add_argument("character"); p.add_argument("--count", type=int, default=12)
    p.add_argument("--start", type=int, default=0); p.add_argument("--text"); p.set_defaults(fn=cmd_audition)
    p = sub.add_parser("line"); p.add_argument("character"); p.add_argument("text"); p.add_argument("--out")
    p.set_defaults(fn=cmd_line)
    p = sub.add_parser("script"); p.add_argument("path"); p.set_defaults(fn=cmd_script)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
