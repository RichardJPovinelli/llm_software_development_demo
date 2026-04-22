"""
train.py

Phase 2 — Fine-tune Llama-3-8B on the Pokédex corpus using QLoRA.

Usage:
    python train.py

Outputs:
    models/lora-adapter/   — LoRA adapter weights
    logs/                  — TensorBoard training logs
"""

import json
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)
from trl import SFTConfig, SFTTrainer

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_MODEL = "NousResearch/Meta-Llama-3-8B-Instruct"
DATA_DIR = Path("data")
OUTPUT_DIR = Path("models/lora-adapter")
LOG_DIR = Path("logs")

LORA_RANK = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
LORA_TARGET_MODULES = ["q_proj", "v_proj"]

NUM_EPOCHS = 3
PER_DEVICE_TRAIN_BATCH_SIZE = 4
GRADIENT_ACCUMULATION_STEPS = 4  # effective batch size = 16
LEARNING_RATE = 2e-4
MAX_SEQ_LENGTH = 256
EVAL_STEPS = 100
SAVE_STEPS = 200

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_jsonl(path: Path) -> Dataset:
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    # Combine prompt + completion into a single "text" field for SFTTrainer
    texts = [r["prompt"] + r["completion"] for r in records]
    return Dataset.from_dict({"text": texts})


def verify_gpu():
    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA is not available. Ensure the CUDA-enabled torch build is installed "
            "and an NVIDIA GPU is present."
        )
    name = torch.cuda.get_device_name(0)
    vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
    print(f"GPU: {name} ({vram_gb:.1f} GB VRAM)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    verify_gpu()

    print("Loading datasets...")
    train_dataset = load_jsonl(DATA_DIR / "train.jsonl")
    val_dataset = load_jsonl(DATA_DIR / "val.jsonl")
    print(f"  Train: {len(train_dataset)} records")
    print(f"  Val:   {len(val_dataset)} records")

    print(f"Loading base model: {BASE_MODEL}")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=False,
    )
    model = prepare_model_for_kbit_training(model)

    print("Applying LoRA config...")
    lora_config = LoraConfig(
        r=LORA_RANK,
        lora_alpha=LORA_ALPHA,
        target_modules=LORA_TARGET_MODULES,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    training_args = SFTConfig(
        output_dir=str(OUTPUT_DIR),
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=PER_DEVICE_TRAIN_BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        learning_rate=LEARNING_RATE,
        fp16=False,
        bf16=True,
        logging_dir=str(LOG_DIR),
        logging_steps=EVAL_STEPS,
        eval_strategy="steps",
        eval_steps=EVAL_STEPS,
        save_steps=SAVE_STEPS,
        save_total_limit=2,
        load_best_model_at_end=True,
        report_to="tensorboard",
        warmup_ratio=0.03,
        lr_scheduler_type="cosine",
        optim="paged_adamw_8bit",
        max_length=MAX_SEQ_LENGTH,
        dataset_text_field="text",
        packing=False,
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        processing_class=tokenizer,
    )

    print(f"Starting training for {NUM_EPOCHS} epochs...")
    trainer.train()

    print(f"Saving LoRA adapter to {OUTPUT_DIR}...")
    trainer.model.save_pretrained(str(OUTPUT_DIR))
    tokenizer.save_pretrained(str(OUTPUT_DIR))

    print("Training complete.")


if __name__ == "__main__":
    main()
