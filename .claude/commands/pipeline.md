---
description: Run a Little Ninja Safety Academy pipeline stage (voice | scout | study | ideate | script | cut | review | status)
argument-hint: <stage> [topic, url, script id, or stats]
---

Stage requested: $ARGUMENTS

1. Re-read `CLAUDE.md` (and any files in `frameworks/`, which override it).
2. Session-start check (CLAUDE.md §8): last 10 rows of `published/log.csv`, `ideas/backlog.md`, `ideas/insights.md`.
3. Map the first word of the arguments to a stage in CLAUDE.md §5:
   - `voice` → 0 · VOICE
   - `scout` → 1 · SCOUT (rest of args = topic)
   - `study` → 2 · STUDY (rest of args = reference Short URL or local file)
   - `ideate` → 3 · IDEATE
   - `script` → 4 · SCRIPT (rest of args = backlog idea or id)
   - `cut` → 5 · CUT & PRODUCE (rest of args = script id)
   - `review` → 6 · REVIEW (rest of args = script id or pasted stats)
   - `status` → no stage: summarize what exists in each folder, which scripts sit at which status, and the single best next step.
   - No / unknown stage → show this list and ask which one.
4. Before writing a script, confirm the character brackets in CLAUDE.md §1 are filled. If not, ask for them in one question.
5. Run the stage exactly as written, saving outputs to the folders in §4. Apply the §7 guardrails to anything kid-facing.
6. End with: files written, anything blocked or faked-avoided, and the next `/pipeline` command to run.
