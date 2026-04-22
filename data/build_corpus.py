"""
build_corpus.py

Phase 1 — Step 2: Process cached raw PokeAPI responses into a fine-tuning
corpus (JSONL), then split into train/val/test sets.

Usage:
    python data/build_corpus.py

Outputs:
    data/pokedex_finetune.jsonl   — full corpus
    data/train.jsonl              — 80%
    data/val.jsonl                — 10%
    data/test.jsonl               — 10%
"""

import json
import random
from pathlib import Path

RAW_DIR = Path(__file__).parent / "raw"
DATA_DIR = Path(__file__).parent

MIN_ENTRY_LENGTH = 20  # characters; shorter entries are likely stubs
RANDOM_SEED = 42

# PokeAPI shape names that map to more human-readable terms
SHAPE_MAP = {
    "ball": "round",
    "squiggle": "squiggly",
    "fish": "fish-like",
    "arms": "upright with arms",
    "blob": "blob-like",
    "upright": "upright",
    "legs": "legged",
    "quadruped": "quadruped",
    "wings": "winged",
    "tentacles": "tentacled",
    "heads": "multi-headed",
    "humanoid": "humanoid",
    "bug-wings": "winged insect",
    "armor": "armored",
}


def load_json(path: Path) -> dict | None:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def get_english(entries: list[dict], key: str = "name") -> str:
    """Extract English value from a list of language-keyed dicts."""
    for entry in entries:
        if entry.get("language", {}).get("name") == "en":
            return entry.get(key, "")
    return ""


def build_description(species: dict, types: list[str]) -> str:
    """
    Synthesize a natural-language description from species metadata.
    Pulls: color, shape, habitat, genera, and types.
    """
    parts = []

    color = species.get("color", {}).get("name", "")
    shape_raw = (species.get("shape") or {}).get("name", "")
    shape = SHAPE_MAP.get(shape_raw, shape_raw.replace("-", " "))
    habitat = (species.get("habitat") or {}).get("name", "")
    genera = get_english(species.get("genera", []), key="genus")
    type_str = " and ".join(types) if types else ""

    # Build a compact but varied description
    if shape and color:
        parts.append(f"A {color}, {shape}")
    elif color:
        parts.append(f"A {color}")
    elif shape:
        parts.append(f"A {shape}")
    else:
        parts.append("A")

    if type_str:
        parts.append(f"{type_str}-type")

    if genera:
        parts.append(f"Pokémon ({genera})")
    else:
        parts.append("Pokémon")

    if habitat:
        parts.append(f"found in {habitat.replace('-', ' ')} areas")

    return " ".join(parts) + "."


def build_records(species: dict, types: list[str]) -> list[dict]:
    """Build one fine-tuning record per English flavor text entry."""
    name = species.get("name", "").capitalize()
    type_str = ", ".join(t.capitalize() for t in types) if types else "Unknown"
    description = build_description(species, types)

    records = []
    seen_texts = set()

    for entry in species.get("flavor_text_entries", []):
        if entry.get("language", {}).get("name") != "en":
            continue

        # Clean flavor text: remove newlines and form-feed characters
        text = entry.get("flavor_text", "").replace("\n", " ").replace("\f", " ").strip()
        # Collapse multiple spaces
        text = " ".join(text.split())

        if len(text) < MIN_ENTRY_LENGTH:
            continue
        if text in seen_texts:
            continue
        seen_texts.add(text)

        prompt = (
            f"[Description]: {description}\n"
            f"[Name]: {name}\n"
            f"[Type]: {type_str}\n"
            f"[Entry]:"
        )
        records.append({"prompt": prompt, "completion": f" {text}"})

    return records


def split_and_save(records: list[dict]):
    """Shuffle and split into 80/10/10 train/val/test."""
    random.seed(RANDOM_SEED)
    random.shuffle(records)

    n = len(records)
    train_end = int(n * 0.8)
    val_end = train_end + int(n * 0.1)

    splits = {
        "train": records[:train_end],
        "val": records[train_end:val_end],
        "test": records[val_end:],
    }

    for split_name, split_records in splits.items():
        path = DATA_DIR / f"{split_name}.jsonl"
        with path.open("w", encoding="utf-8") as f:
            for record in split_records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"  {split_name}.jsonl: {len(split_records)} records")

    return splits


def main():
    print("Building corpus from cached raw data...")

    species_files = sorted(
        p for p in RAW_DIR.glob("*.json") if not p.stem.endswith("_pokemon")
    )

    if not species_files:
        print("ERROR: No cached species files found in data/raw/. Run fetch_data.py first.")
        return

    all_records = []
    processed = 0
    skipped = 0

    for species_path in species_files:
        species = load_json(species_path)
        if species is None:
            skipped += 1
            continue

        name = species.get("name", "")
        pokemon_path = RAW_DIR / f"{name}_pokemon.json"
        pokemon_data = load_json(pokemon_path)
        types = (
            [t["type"]["name"] for t in pokemon_data.get("types", [])]
            if pokemon_data
            else []
        )

        records = build_records(species, types)
        all_records.extend(records)
        processed += 1

    print(f"Processed {processed} species, skipped {skipped}.")
    print(f"Total records before split: {len(all_records)}")

    if len(all_records) < 4000:
        print(
            f"WARNING: Only {len(all_records)} records — below the 4,000 target. "
            "Consider lowering MIN_ENTRY_LENGTH to 10 in build_corpus.py."
        )

    # Save full corpus
    corpus_path = DATA_DIR / "pokedex_finetune.jsonl"
    with corpus_path.open("w", encoding="utf-8") as f:
        for record in all_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"Saved full corpus to: {corpus_path}")

    # Save splits
    print("Splitting into train/val/test (80/10/10)...")
    split_and_save(all_records)

    print(f"\nSummary:")
    print(f"  Species processed : {processed}")
    print(f"  Total records     : {len(all_records)}")
    print(f"  Min entry length  : {MIN_ENTRY_LENGTH} chars")
    print(f"  Output dir        : {DATA_DIR}")


if __name__ == "__main__":
    main()
