"""
fetch_data.py

Phase 1 — Step 1: Fetch all Pokémon species data from PokeAPI and cache raw
JSON responses to data/raw/. Safe to re-run; already-cached species are skipped.

Usage:
    python data/fetch_data.py
"""

import json
import time
from pathlib import Path

import requests

BASE_URL = "https://pokeapi.co/api/v2"
RAW_DIR = Path(__file__).parent / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

REQUEST_DELAY = 0.05  # seconds between requests (~20 req/s, well within limits)
SESSION = requests.Session()


def get_json(url: str) -> dict:
    response = SESSION.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_all_species() -> list[dict]:
    """Return the list of all species stubs from the paginated species endpoint."""
    species_list = []
    url = f"{BASE_URL}/pokemon-species?limit=100&offset=0"
    while url:
        data = get_json(url)
        species_list.extend(data["results"])
        url = data.get("next")
        time.sleep(REQUEST_DELAY)
    return species_list


def fetch_species_detail(name: str) -> dict | None:
    """Fetch full species detail. Returns None on error."""
    cache_path = RAW_DIR / f"{name}.json"
    if cache_path.exists():
        with cache_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    try:
        data = get_json(f"{BASE_URL}/pokemon-species/{name}")
        with cache_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        time.sleep(REQUEST_DELAY)
        return data
    except requests.HTTPError as e:
        print(f"  WARNING: HTTP error for {name}: {e}")
        return None


def fetch_pokemon_types(name: str) -> list[str]:
    """Fetch type names for a Pokémon (from the pokemon endpoint, not species)."""
    cache_path = RAW_DIR / f"{name}_pokemon.json"
    if cache_path.exists():
        with cache_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        try:
            data = get_json(f"{BASE_URL}/pokemon/{name}")
            with cache_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            time.sleep(REQUEST_DELAY)
        except requests.HTTPError:
            return []

    return [t["type"]["name"] for t in data.get("types", [])]


def main():
    print("Fetching species list...")
    species_list = fetch_all_species()
    total = len(species_list)
    print(f"Found {total} species.")

    fetched = 0
    skipped = 0
    errors = 0

    for i, stub in enumerate(species_list, 1):
        name = stub["name"]
        cache_path = RAW_DIR / f"{name}.json"
        already_cached = cache_path.exists()

        detail = fetch_species_detail(name)
        if detail is None:
            errors += 1
            continue

        # Also cache the pokemon endpoint for type data
        fetch_pokemon_types(name)

        if already_cached:
            skipped += 1
        else:
            fetched += 1

        if i % 100 == 0 or i == total:
            print(f"  [{i}/{total}] fetched={fetched} skipped={skipped} errors={errors}")

    print(f"\nDone. Total: {total}, newly fetched: {fetched}, from cache: {skipped}, errors: {errors}")
    print(f"Raw data saved to: {RAW_DIR}")


if __name__ == "__main__":
    main()
