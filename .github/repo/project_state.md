# Project State

**Project:** Generation-Based Pokémon Name & Lore Creator  
**Date:** 2026-04-22  
**Status:** Planning

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
- [ ] Set up training environment (`transformers`, `peft`, `bitsandbytes`, `trl`, `accelerate`)
- [ ] Write `train.py`: load Llama-3-8B in 4-bit, apply QLoRA, train with `SFTTrainer`, save LoRA adapter to `models/lora-adapter/`
- [ ] Write `merge.py`: merge LoRA adapter into base model, save to `models/merged/`
- [ ] Write `evaluate.py`: run inference on test set, review 10 sample outputs
- [ ] Export merged model to GGUF (Q4_K_M) using `llama.cpp`, save to `models/pokedex-llama3-8b-q4.gguf`
- [ ] Load GGUF into LM Studio and verify it loads without errors

### Phase 3 — Inference Interface
- [ ] Build a Gradio app that calls LM Studio's OpenAI-compatible endpoint
- [ ] Input: user description → Output: generated name, type, Pokédex entry
- [ ] Add basic output validation/filtering

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

