"""
evaluate.py

Phase 2 — Evaluate the fine-tuned model against the test set.

Prints 10 sample completions side-by-side with ground truth and computes
average output length as a sanity metric.

Usage:
    python evaluate.py [--model MODEL_PATH]

Arguments:
    --model   Path to the model directory (default: models/lora-adapter).
              After merging, you can point this at models/merged instead.
"""

import argparse
import json
import random
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

DATA_PATH = Path("data/test.jsonl")
DEFAULT_MODEL = "models/lora-adapter"
NUM_SAMPLES = 10
MAX_NEW_TOKENS = 128
RANDOM_SEED = 42


def load_test_samples(path: Path, n: int) -> list[dict]:
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    random.seed(RANDOM_SEED)
    return random.sample(records, min(n, len(records)))


def load_model(model_path: str):
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        quantization_config=bnb_config,
        device_map="auto",
    )
    model.eval()
    return model, tokenizer


def generate(model, tokenizer, prompt: str) -> str:
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            temperature=1.0,
            repetition_penalty=1.1,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id,
        )
    # Decode only the newly generated tokens
    new_ids = output_ids[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(new_ids, skip_special_tokens=True).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model directory path")
    args = parser.parse_args()

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Test data not found: {DATA_PATH}. Run data/build_corpus.py first.")

    print(f"Loading model from: {args.model}")
    model, tokenizer = load_model(args.model)

    print(f"Sampling {NUM_SAMPLES} records from {DATA_PATH}...")
    samples = load_test_samples(DATA_PATH, NUM_SAMPLES)

    generated_lengths = []
    passed = 0

    print("\n" + "=" * 80)
    for i, sample in enumerate(samples, 1):
        prompt = sample["prompt"]
        ground_truth = sample["completion"].strip()
        generated = generate(model, tokenizer, prompt)
        generated_lengths.append(len(generated.split()))

        # Extract just the description line for a compact header
        desc_line = next(
            (l for l in prompt.splitlines() if l.startswith("[Description]")), ""
        )

        print(f"\nSample {i}/10")
        print(f"  {desc_line}")
        print(f"  GROUND TRUTH : {ground_truth}")
        print(f"  GENERATED    : {generated}")

        # Rough quality check: non-empty and at least 5 words
        if len(generated.split()) >= 5:
            passed += 1

    avg_len = sum(generated_lengths) / len(generated_lengths) if generated_lengths else 0

    print("\n" + "=" * 80)
    print(f"Results:")
    print(f"  Samples evaluated  : {NUM_SAMPLES}")
    print(f"  Passed quality bar : {passed}/{NUM_SAMPLES} (≥5 words, non-empty)")
    print(f"  Avg output length  : {avg_len:.1f} words")

    if passed < 8:
        print(
            "\nWARNING: Fewer than 8/10 samples passed. "
            "Consider training for more epochs or adjusting hyperparameters. "
            "See the fallback option in .github/prompts/phase-2-fine-tuning.prompt.md."
        )
    else:
        print("\nQuality bar met. Proceed to GGUF export (see models/README.md).")


if __name__ == "__main__":
    main()
