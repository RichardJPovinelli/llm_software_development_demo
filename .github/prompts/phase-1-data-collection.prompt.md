# Phase 1 — Data Collection & Preparation

## Objective
Pull Pokédex entry text and supporting metadata from PokeAPI, clean it, and format it into a fine-tuning corpus of prompt→completion pairs that the model can learn from.

## Context
- All project decisions are in `.github/repo/decisions.md`.
- Active task state is in `.github/repo/project_state.md`.
- The fine-tuning prompt format (DEC-004) is:
  ```
  [Description]: <synthesized from name + type>
  [Name]: <Pokémon name>
  [Type]: <type(s)>
  [Entry]: <Pokédex text>
  ```
- Because real Pokédex entries do not come with user-written descriptions, the `[Description]` field must be synthesized. A simple template is sufficient (e.g., "A <type> Pokémon named <name>").

## Tasks
1. Write a Python script to fetch all Pokémon from PokeAPI (`/api/v2/pokemon-species`).
2. For each species, pull:
   - Name
   - Type(s)
   - All English Pokédex flavor text entries (across game versions)
3. Retain all flavor text entries per species per game version — do **not** deduplicate across versions. This maximizes corpus size (target: 5,000+ records across ~1,025 species).
4. Synthesize a `[Description]` field that goes beyond name + type. Pull additional fields from PokeAPI to make descriptions richer and closer to what a user might type:
   - `shape` (e.g., "quadruped", "blob")
   - `color`
   - `habitat` (if available)
   - `genera` (the short category, e.g., "Flame Pokémon")
   Example output: `"A small, quadruped fire Pokémon, red and orange in color, found in mountains."`
5. Format each record as a fine-tuning example (one JSON object per entry):
   ```json
   {
     "prompt": "[Description]: A fire Pokémon named Charmander\n[Name]: Charmander\n[Type]: Fire\n[Entry]:",
     "completion": " Obviously prefers hot places. When it rains, steam is said to spout from the tip of its tail."
   }
   ```
6. Save the dataset as `data/pokedex_finetune.jsonl`.
7. Perform an 80/10/10 train/validation/test split and save as `data/train.jsonl`, `data/val.jsonl`, `data/test.jsonl`.

## Constraints
- Use only the English flavor text (`language.name == "en"`).
- Do not include flavor text shorter than 20 characters (some entries are stubs).
- Rate-limit PokeAPI requests (no more than 100 requests/second); use a small `time.sleep` or `asyncio` throttle.
- Store raw API responses in `data/raw/` before processing, so the pipeline can be re-run without re-fetching.

## Files to Inspect
- `.github/repo/decisions.md` — DEC-002 (data source), DEC-004 (prompt format)
- `.github/repo/project_state.md` — Phase 1 task list

## Risks & Mitigations
- **Corpus too small:** Retaining all per-version flavor text (rather than deduplicating) and enriching the description field maximizes usable training examples. If final corpus is below 4,000 records after filtering, consider lowering the minimum length filter from 20 to 10 characters.
- **Description distribution mismatch:** Enriching the `[Description]` field with shape, color, habitat, and genera (rather than just name + type) narrows the gap between training descriptions and real user inputs like "A spicy blue cat".

## Definition of Done
- [ ] `data/raw/` contains cached PokeAPI responses.
- [ ] `data/pokedex_finetune.jsonl` exists with at least 5,000 records.
- [ ] Descriptions include shape, color, and habitat fields where available.
- [ ] `data/train.jsonl`, `data/val.jsonl`, `data/test.jsonl` exist with correct splits.
- [ ] A brief summary of record counts is printed on script completion.
