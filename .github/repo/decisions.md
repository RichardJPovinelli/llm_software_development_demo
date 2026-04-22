# Decisions

**Project:** Generation-Based Pokémon Name & Lore Creator  
**Date:** 2026-04-22

---

## DEC-001 — Dual-document planning structure
**Date:** 2026-04-22  
**Decision:** Use both `project_state.md` (progress tracking) and `decisions.md` (architectural/workflow decisions) as per `copilot-instructions.md`.  
**Rationale:** The project spans multiple phases (data, training, inference, UI) and will involve non-trivial architectural choices that benefit from a dedicated log.

---

## DEC-002 — Primary data source: PokeAPI
**Date:** 2026-04-22  
**Decision:** Use PokeAPI as the primary source for Pokédex entry text.  
**Rationale:** It is the most comprehensive, structured, and freely accessible source for canonical Pokédex text across all generations. Kaggle dataset supplements with tabular stats/types.  
**Alternatives considered:** Veekun (CSV-based, more complex to parse); scraping Bulbapedia (licensing risk).

---

## DEC-003 — Base model: Llama-3-8B
**Date:** 2026-04-22  
**Decision:** Use Llama-3-8B as the base model. Fine-tune with QLoRA on the local A4000.  
**Rationale:** Hardware is confirmed as NVIDIA A4000 (16GB VRAM) with 128GB RAM. Llama-3-8B in 4-bit quantization (~5GB VRAM active) fits comfortably. QLoRA fine-tuning on the A4000 is well-supported by libraries like `transformers` + `peft` + `bitsandbytes`. GPT-2 is no longer necessary as a fallback.  
**Alternatives considered:** GPT-2 (lower quality, no longer needed given available hardware); larger models (13B+) possible but offer diminishing returns for this task.

---

## DEC-005 — Inference host: LM Studio with OpenAI-compatible API
**Date:** 2026-04-22  
**Decision:** Use LM Studio to host the fine-tuned model locally. The application communicates with it via LM Studio's OpenAI-compatible REST API.  
**Rationale:** LM Studio provides a zero-infrastructure local inference server with an API that mirrors the OpenAI SDK, minimizing integration complexity. The fine-tuned model will be exported to GGUF format (quantized) for loading into LM Studio.  
**Implications:**
- Fine-tuning and export are separate steps from serving.
- The application code uses the `openai` Python SDK pointed at `http://localhost:<port>`.
- No cloud API keys or costs required for inference.

---

## DEC-006 — Interface: web front-end
**Date:** 2026-04-22  
**Decision:** Include a web front-end in addition to (or instead of) a CLI.  
**Rationale:** More accessible for seminar demos; allows non-technical attendees to interact with the tool directly in a browser.  
**Stack:** Gradio (serves both the UI and calls the LM Studio API directly — no separate FastAPI layer needed).  
**Rationale:** Gradio eliminates the need for a separate backend; it runs as a Python app, calls the LM Studio OpenAI-compatible endpoint, and renders the UI in the browser. Minimal code, well-suited for seminar demos.

---

## DEC-004 — Prompt format
**Date:** 2026-04-22  
**Decision (proposed):** Structure fine-tuning examples as:  
```
[Description]: <user input>
[Name]: <Pokémon name>
[Type]: <type(s)>
[Entry]: <Pokédex text>
```
**Rationale:** Explicit field labels help the model learn structured generation and make inference-time prompting predictable.  
**Status:** Proposed — confirm before fine-tuning begins.

---

## DEC-007 — Use ungated Llama-3 mirror for training
**Date:** 2026-04-22  
**Decision:** Use `NousResearch/Meta-Llama-3-8B-Instruct` as the training base model in place of `meta-llama/Meta-Llama-3-8B-Instruct`.  
**Rationale:** The active Hugging Face account has a valid token but does not have gated access approval for the Meta-hosted repository, causing 403 errors at model download time. The NousResearch mirror provides the same architecture/weights family and unblocks local QLoRA fine-tuning workflow immediately.  
**Implications:**
- `train.py` and `merge.py` use the ungated model ID.
- Repro steps should mention this model ID unless Meta access is later approved.

