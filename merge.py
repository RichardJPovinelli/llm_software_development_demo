"""
merge.py

Phase 2 — Merge the LoRA adapter into the base model to produce a single
full-precision HuggingFace model ready for GGUF conversion.

Usage:
    python merge.py

Inputs:
    models/lora-adapter/   — LoRA adapter saved by train.py

Outputs:
    models/merged/         — Full merged model (bf16)
"""

from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE_MODEL = "NousResearch/Meta-Llama-3-8B-Instruct"
ADAPTER_DIR = Path("models/lora-adapter")
OUTPUT_DIR = Path("models/merged")


def main():
    if not ADAPTER_DIR.exists():
        raise FileNotFoundError(
            f"Adapter directory not found: {ADAPTER_DIR}. Run train.py first."
        )

    print(f"Loading base model: {BASE_MODEL}")
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.bfloat16,
        device_map="cpu",  # merge on CPU to avoid VRAM pressure
        trust_remote_code=False,
    )

    tokenizer = AutoTokenizer.from_pretrained(ADAPTER_DIR)

    print(f"Loading LoRA adapter from: {ADAPTER_DIR}")
    model = PeftModel.from_pretrained(model, str(ADAPTER_DIR))

    print("Merging adapter weights into base model...")
    model = model.merge_and_unload()

    print(f"Saving merged model to: {OUTPUT_DIR}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(OUTPUT_DIR), safe_serialization=True)
    tokenizer.save_pretrained(str(OUTPUT_DIR))

    print("Merge complete.")
    print(f"Merged model saved to: {OUTPUT_DIR}")
    print("Next step: convert to GGUF using llama.cpp (see models/README.md).")


if __name__ == "__main__":
    main()
