# Phase 4 — Demo & Polish

## Objective
Prepare the project for seminar presentation: verify the end-to-end pipeline works reliably, add polish to the Gradio UI, and produce usage documentation.

## Context
- All project decisions are in `.github/repo/decisions.md`.
- Active task state is in `.github/repo/project_state.md`.
- The audience is a seminar — non-technical attendees will interact with the Gradio app live.
- "Wow factor" is tone: outputs should read like original Game Boy Pokédex entries.

## Tasks

### 4a — End-to-End Verification
1. Run the full pipeline from a clean state:
   - LM Studio loaded with `models/pokedex-llama3-8b-q4.gguf`.
   - `python app.py` started.
   - At least 10 test descriptions submitted and outputs reviewed.
2. Document any failure modes observed and apply fixes.

### 4b — UI Polish
1. Add a title and subtitle to the Gradio app ("Pokédex Entry Generator" / "Describe a Pokémon, get a Pokédex entry").
2. Add 3–5 example descriptions as clickable Gradio examples (e.g., "A spicy blue cat", "A tiny ghost that lives in old clocks", "A rock Pokémon shaped like a sleeping bear").
3. Style the output area to display Name and Type prominently before the Entry text.

### 4c — Demo Script
1. Prepare a short demo script (talking points, not code) covering:
   - What the tool does and why it's interesting.
   - How the fine-tuning works at a high level (PokeAPI data → QLoRA → GGUF → LM Studio).
   - 2–3 live demo examples with surprising or funny results.

### 4d — README
1. Write a top-level `README.md` covering:
   - Project overview (one paragraph).
   - Prerequisites (Python version, LM Studio, CUDA).
   - Setup instructions (install deps, configure `.env`, load GGUF into LM Studio, run app).
   - How to reproduce fine-tuning (point to Phase 1 and Phase 2 scripts).

### 4e — Repository Cleanup
1. Confirm `models/` and `data/raw/` are in `.gitignore`.
2. Confirm `data/train.jsonl`, `data/val.jsonl`, `data/test.jsonl` are either committed or documented as reproducible from the fetch script.
3. Remove any debug print statements from `app.py` and data scripts.

## Constraints
- Do not over-engineer the UI — Gradio defaults are acceptable; only polish what is visible during the demo.
- The README must be accurate and runnable by someone who was not involved in development.

## Files to Inspect
- `.github/repo/project_state.md` — all phases (verify all tasks are marked complete)
- `.github/repo/decisions.md` — full decision log (use as source of truth for README)
- All prior phase prompt files for script names and expected outputs

## Definition of Done
- [ ] 10 test descriptions produce acceptable outputs with no crashes.
- [ ] Gradio app has title, subtitle, and example inputs.
- [ ] `README.md` exists at repo root and covers setup end-to-end.
- [ ] `.gitignore` excludes `models/` and `data/raw/`.
- [ ] Project is ready to demo live in a seminar setting.
