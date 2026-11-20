# Free Voiceovers: playbook

Goal: $0 voiceover for every Short, made on your own machine, with a paid voice only when it's worth it.

## The free ladder (best ROI first)
| Rank | Option | Cost | Quality for kids content | Notes |
|---|---|---|---|---|
| 1 | **Your own voice / a family member** (phone + closet = free vocal booth) | $0 | ★★★★★ | Most trustworthy to parents. Needs **no AI label**. Pitch Kiko and Zip up with the same FFmpeg chain `vo.py` uses. |
| 2 | **Piper TTS** (`tools/vo.py`, set up in this repo) | $0, offline | ★★★☆☆ | Fast, unlimited, private. Robotic on long lines, so keep sentences short (which you want anyway). |
| 3 | Canva / CapCut built-in text-to-speech | $0 on free tiers (limits change) | ★★★☆☆ | Check each app's current commercial-use terms. |
| 4 | Paid (ElevenLabs etc.) | credits | ★★★★★ | Only after a format proves itself in `published/log.csv`. CLAUDE.md says to confirm before spending. |

**Pro move:** Piper for drafts and timing, then re-record the winners in your own voice. The script is locked before anyone spends studio time.

## One-time setup (on your computer)
```bash
pip install piper-tts          # FFmpeg also required
python tools/vo.py setup       # downloads the free voices into tools/voices/ (git-ignored)
```

## Cast each character (10 minutes, once)
```bash
python tools/vo.py audition kiko --count 20          # 20 takes of Kiko's line, speakers 0–19
python tools/vo.py audition "sensei hoot" --start 20 --count 20
python tools/vo.py audition zip
```
Listen in `audio/auditions/`, then put the winning speaker id into `tools/cast_voices.json`.
Tweak `pitch` (semitones), `tempo`, and `length_scale` (above 1 = slower, clearer speech: good for ages 4–8).

## Every Short
In `scripts/###-slug.md`, write VO lines like this:
```
  SOUND / VO: KIKO: "Ninja eyes ON!"
  VO: SENSEI HOOT: "A true ninja stays calm and gets a grown-up."
  ZIP: "Light on! Stop and think!"
  NARRATOR: Stop! Think! Ninja safe!
```
Then run `python tools/vo.py script scripts/001-slug.md` to get `audio/vo/001-vo.wav` at -14 LUFS.
It prints words per second; aim for about 2 (CLAUDE.md §5 stage 4).

## Rules that still apply
- **AI label (§7.8):** Piper voices are synthetic. Turn on TikTok's AI-generated label and YouTube's altered/synthetic setting. Your own recorded voice needs neither.
- **License:** each Piper voice inherits its training-data license. LJSpeech is public domain and LibriTTS-R is CC BY 4.0 (credit it in the description). **Read each voice's MODEL_CARD at huggingface.co/rhasspy/piper-voices before monetized use**, and skip any marked non-commercial (NC).
- Never clone a real person's voice without their written OK.
