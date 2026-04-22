# Phase 2 — Fine-Tuning & Model Export

## Objective
Fine-tune Llama-3-8B on the Pokédex corpus using QLoRA, evaluate the output quality, and export the resulting model to GGUF format for loading into LM Studio.

## Context
- All project decisions are in `.github/repo/decisions.md`.
- Active task state is in `.github/repo/project_state.md`.
- Hardware: NVIDIA A4000 (16GB VRAM), 128GB system RAM.
- Base model: `meta-llama/Meta-Llama-3-8B` (or instruction-tuned variant `Meta-Llama-3-8B-Instruct`).
- Fine-tuning method: QLoRA (4-bit quantization via `bitsandbytes`, LoRA adapters via `peft`).
- Training framework: Hugging Face `transformers` + `trl` (`SFTTrainer`).
- Dataset produced by Phase 1: `data/train.jsonl`, `data/val.jsonl`.

## Tasks

### 2a — Environment Setup
1. Create `requirements-train.txt` with: `transformers`, `peft`, `bitsandbytes`, `trl`, `datasets`, `accelerate`, `torch` (CUDA build).
2. Verify GPU is visible: `torch.cuda.is_available()` and `torch.cuda.get_device_name(0)`.

### 2b — Fine-Tuning Script
1. Write `train.py`:
   - Load `data/train.jsonl` and `data/val.jsonl` using Hugging Face `datasets`.
   - Load Llama-3-8B in 4-bit with `BitsAndBytesConfig`.
   - Apply LoRA config via `peft` (target modules: `q_proj`, `v_proj`; rank 16; alpha 32).
   - Train with `SFTTrainer` for 3 epochs, logging val loss every 100 steps.
   - Save LoRA adapter weights to `models/lora-adapter/`.
2. Write `merge.py`:
   - Load base model + LoRA adapter and merge them into a single full-precision model.
   - Save merged model to `models/merged/`.

### 2c — Evaluation
1. Write `evaluate.py`:
   - Run inference on `data/test.jsonl` prompts.
   - Print 10 sample outputs side-by-side with ground truth.
   - Compute average output length as a basic sanity metric.

### 2d — GGUF Export
1. Pin the `llama.cpp` commit used for conversion and record it in `models/README.md` (the conversion script changes frequently; pinning ensures reproducibility).
2. Use `llama.cpp`'s `convert_hf_to_gguf.py` to convert `models/merged/` to GGUF.
3. Quantize to Q4_K_M using `llama-quantize`.
4. Save output to `models/pokedex-llama3-8b-q4.gguf`.
5. Load the GGUF into LM Studio and verify it loads without errors.
6. **Do not leave GGUF export until the end.** Run a dry-run conversion on the base model (before fine-tuning) to confirm the toolchain works.

## Constraints
- Do not fine-tune the full model weights — use LoRA adapters only.
- Keep LoRA rank ≤ 32 to stay within VRAM budget.
- Do not commit model weights or GGUF files to the repository; add `models/` to `.gitignore`.
- Log all training runs (loss curves) to `logs/` for reproducibility.

## Files to Inspect
- `.github/repo/decisions.md` — DEC-003 (model), DEC-004 (prompt format), DEC-005 (LM Studio)
- `.github/repo/project_state.md` — Phase 2 task list
- `.github/prompts/phase-1-data-collection.prompt.md` — expected data format

## Risks & Mitigations
- **GGUF export toolchain fragility:** Pin the `llama.cpp` commit and run a dry-run export on the base model early (task 2d step 6) before investing time in fine-tuning.
- **Fine-tuning quality insufficient for demo:** Define a minimum bar — at least 8 of 10 test outputs must read as plausible Pokédex entries. If not met after 3 epochs, try: increasing epochs to 5, raising LoRA rank to 32, or broadening the corpus. **Fallback:** if fine-tuning cannot meet the bar, use base `Meta-Llama-3-8B-Instruct` with a carefully crafted system prompt in Phase 3 instead of a fine-tuned model.

## Definition of Done
- [ ] GGUF toolchain dry-run succeeds on base model before fine-tuning begins.
- [ ] `train.py` runs to completion without OOM errors.
- [ ] LoRA adapter saved to `models/lora-adapter/`.
- [ ] Merged model saved to `models/merged/`.
- [ ] `evaluate.py` produces readable, Pokédex-style completions for at least 8 of 10 test samples.
- [ ] `models/pokedex-llama3-8b-q4.gguf` exists and loads successfully in LM Studio.
- [ ] `llama.cpp` commit hash recorded in `models/README.md`.
