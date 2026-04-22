# Project State

**Project:** Generation-Based Pokémon Name & Lore Creator  
**Date:** 2026-04-22  
**Status:** Phase 3 Complete

---

## Goal

Build a tool that accepts a short natural-language description (e.g., "A spicy blue cat") and generates a plausible Pokémon name, type(s), and a Pokédex entry that sounds authentic to the original Game Boy games.

---

## Phases

### Phase 1 — Data Collection & Preparation ✅
- [x] Pull Pokédex entry text from PokeAPI (all generations) — `data/fetch_data.py`
- [x] Supplement with Kaggle Pokémon dataset (stats, types, names) — types pulled via PokeAPI pokemon endpoint
- [x] Clean and format text into fine-tuning corpus (prompt → entry pairs) — `data/build_corpus.py`
- [x] Run `fetch_data.py` — 1,025 species fetched, 0 errors
- [x] Run `build_corpus.py` — 8,490 records; train=6,792 / val=849 / test=849

### Phase 2 — Fine-Tuning & Model Export
- [x] Set up training environment (`transformers`, `peft`, `bitsandbytes`, `trl`, `accelerate`) — `requirements-train.txt`
- [x] Write `train.py`: load Llama-3-8B in 4-bit, apply QLoRA, train with `SFTTrainer`, save LoRA adapter to `models/lora-adapter/`
- [x] Write `merge.py`: merge LoRA adapter into base model, save to `models/merged/`
- [x] Write `evaluate.py`: run inference on test set, review 10 sample outputs
- [x] Document GGUF export steps — `models/README.md` (pinned llama.cpp commit: b3796)
- [x] **Install training deps** (`pip install torch --index-url ... && pip install -r requirements-train.txt`)
- [ ] **Run dry-run GGUF export** on base model (confirms toolchain before training)
- [x] **Run `train.py`** to fine-tune
- [x] **Run `merge.py`** to merge adapter
- [x] **Run `evaluate.py`** to verify quality (target: 8/10 samples)
- [x] **Export to GGUF** (`models/pokedex-llama3-8b-f16.gguf` → `models/pokedex-llama3-8b-q4.gguf`) and load into LM Studio

### Phase 3 — Inference Interface
- [x] Build a Gradio app that calls LM Studio's OpenAI-compatible endpoint — `app.py`
- [x] Input: user description → Output: generated name, type, Pokédex entry
- [x] Add basic output validation/filtering — `parse_completion()` in `utils.py` with fallback strings
- [x] Config externalized to `config.py` + `.env` (LM_STUDIO_BASE_URL, LM_STUDIO_MODEL)
- [x] `requirements-app.txt` created (gradio, openai, python-dotenv)
- [x] **Run task 3a** — LM Studio API compatibility verified (`client.models.list()` succeeds via `http://localhost:1234/v1`)

### Phase 4 — Demo & Polish
- [ ] Prepare demo examples for seminar presentation
- [ ] Document usage and model training steps

---

## Open Questions

- ~~What compute is available?~~ **Resolved:** NVIDIA A4000 (16GB VRAM), 128GB RAM. Llama-3-8B with QLoRA fine-tuning is viable.
- ~~Should the interface be CLI-only or include a web front-end?~~ **Resolved:** Include a web front-end.
- Is multilingual output (e.g., Japanese-style names) in scope?

---

## Notes

- PokeAPI is the primary data source for Pokédex text.
- The "wow factor" is tone: outputs should read like original 8-bit Game Boy entries (terse, biological, slightly ominous).
- **Inference host:** LM Studio (local, OpenAI-compatible API). The application calls LM Studio as it would call OpenAI.
- **Hardware:** NVIDIA A4000 (16GB VRAM), 128GB system RAM. Fine-tuning via QLoRA on the A4000 is feasible for Llama-3-8B.
- **Serving model:** Fine-tuned GGUF (quantized) loaded into LM Studio post-training.
- **Base model used for training:** `NousResearch/Meta-Llama-3-8B-Instruct` (ungated mirror of Llama-3-8B-Instruct) due gated-access restrictions on the Meta repository for the current account.
- **Training result (Phase 2):** `train.py` completed 3 epochs successfully; final train loss ~1.149, eval loss ~1.071, eval mean token accuracy ~0.75.
- **Evaluation result:** `evaluate.py` passed 10/10 samples on the current quality bar.
- **LM Studio API check (task 3a):** Passed with `openai` Python SDK v1+ (`client.models.list()`), LM Studio CLI version `v0.0.47`.
- **LM Studio load + generation check:** `models/pokedex-llama3-8b-q4.gguf` loaded with identifier `pokedex-llama3-8b-q4`; end-to-end `chat.completions.create(...)` returns valid `[Name]/[Type]/[Entry]` output.

