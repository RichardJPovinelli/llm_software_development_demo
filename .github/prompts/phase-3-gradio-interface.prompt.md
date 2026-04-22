# Phase 3 — Gradio Inference Interface

## Objective
Build a Gradio web application that accepts a short user description, sends it to the fine-tuned model hosted in LM Studio, and displays the generated Pokémon name, type(s), and Pokédex entry.

## Context
- All project decisions are in `.github/repo/decisions.md`.
- Active task state is in `.github/repo/project_state.md`.
- LM Studio is running locally and exposes an OpenAI-compatible REST API (default: `http://localhost:1234/v1`).
- The app uses the `openai` Python SDK pointed at the local LM Studio endpoint.
- No API key is required for LM Studio (use a placeholder string like `"lm-studio"`).
- Prompt format (DEC-004):
  ```
  [Description]: <user input>
  [Name]:
  [Type]:
  [Entry]:
  ```
  The model completes the Name, Type, and Entry fields.

## Tasks

### 3a — API Compatibility Check (do this first)
1. Before building the UI, verify LM Studio's API is compatible with the `openai` Python SDK v1+:
   - Start LM Studio, load the GGUF model, and enable the local server.
   - Run a minimal test: `from openai import OpenAI; client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio"); print(client.models.list())`.
   - If this fails, check the LM Studio version and update or adjust the SDK call accordingly before proceeding.
   - Record the working LM Studio version in `.env` comments or `config.py`.

### 3b — Application Script
1. Create `app.py` using Gradio.
2. UI layout:
   - **Input:** Single text box — "Describe your Pokémon" (e.g., "A spicy blue cat").
   - **Output:** Three separate text fields: Name, Type, Entry.
   - **Button:** "Generate".
3. On submit:
   - Build the prompt using the DEC-004 format.
   - Call LM Studio via `openai.ChatCompletion.create` (or `client.chat.completions.create` for SDK v1+).
   - Parse the completion text to extract Name, Type, and Entry fields.
   - Display them in their respective output components.
4. Add a simple system prompt to reinforce the Game Boy Pokédex tone (terse, biological, slightly ominous).

### 3c — Configuration
1. Store the LM Studio base URL and model name in a `config.py` or `.env` file (not hardcoded in `app.py`).
2. Use `python-dotenv` to load `.env` if present.

### 3d — Output Parsing
1. Write a `parse_completion(text)` helper that extracts the `[Name]`, `[Type]`, and `[Entry]` fields from the model's raw completion text.
2. Handle cases where the model omits a field or produces malformed output — return a fallback string (e.g., `"(not generated)"`) rather than crashing.

### 3e — Requirements
1. Create `requirements-app.txt` with: `gradio`, `openai`, `python-dotenv`.

## Constraints
- Do not hardcode the LM Studio URL or model name in `app.py`.
- The app must not crash on malformed model output — use the `parse_completion` fallback.
- Keep `app.py` under 150 lines; extract helpers to `utils.py` if needed.
- Do not store or log user inputs.

## Files to Inspect
- `.github/repo/decisions.md` — DEC-004 (prompt format), DEC-005 (LM Studio API), DEC-006 (Gradio)
- `.github/repo/project_state.md` — Phase 3 task list
- `.github/prompts/phase-2-fine-tuning.prompt.md` — model name and GGUF output used in LM Studio

## Risks & Mitigations
- **LM Studio API version mismatch:** Run the API compatibility check (task 3a) before any other work in this phase. If the `openai` SDK v1+ call fails, check whether LM Studio requires the legacy `openai.ChatCompletion` interface or a different endpoint path, and adjust accordingly.

## Definition of Done
- [ ] LM Studio API compatibility verified (task 3a passes) before UI work begins.
- [ ] `app.py` launches with `python app.py` and opens in the browser.
- [ ] A test description (e.g., "A tiny ghost that lives in old clocks") produces a Name, Type, and Entry without error.
- [ ] Malformed or empty model output does not crash the app.
- [ ] LM Studio URL and model name are read from config, not hardcoded.
