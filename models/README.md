# Models

This directory is excluded from version control (see `.gitignore`).

## Expected contents after Phase 2

```
models/
  lora-adapter/       — LoRA adapter weights (output of train.py)
  merged/             — Full merged model in bf16 (output of merge.py)
  pokedex-llama3-8b-q4.gguf  — Quantized GGUF for LM Studio
  README.md           — This file
```

---

## GGUF Export Instructions

### Pinned llama.cpp commit
```
b3796  (https://github.com/ggerganov/llama.cpp/commit/b3796)
```
> **Important:** The `convert_hf_to_gguf.py` script changes frequently. Always use the pinned commit above to ensure reproducibility. Update this value if you intentionally upgrade.

### Step 1 — Clone and build llama.cpp

```bash
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
git checkout b3796
cmake -B build -DGGML_CUDA=ON
cmake --build build --config Release -j
```

### Step 2 — Dry-run (verify toolchain before fine-tuning)

Run this on the base model *before* fine-tuning to confirm the export pipeline works:

```bash
python llama.cpp/convert_hf_to_gguf.py \
  models/merged \
  --outfile models/pokedex-llama3-8b-f16.gguf \
  --outtype f16
```

If this succeeds, the toolchain is confirmed. Proceed with fine-tuning.

### Step 3 — Convert merged model to GGUF (f16)

After `merge.py` has produced `models/merged/`:

```bash
python llama.cpp/convert_hf_to_gguf.py \
  models/merged \
  --outfile models/pokedex-llama3-8b-f16.gguf \
  --outtype f16
```

### Step 4 — Quantize to Q4_K_M

```bash
llama.cpp/build/bin/llama-quantize \
  models/pokedex-llama3-8b-f16.gguf \
  models/pokedex-llama3-8b-q4.gguf \
  Q4_K_M
```

### Step 5 — Load in LM Studio

1. Open LM Studio.
2. Go to **My Models → Import Model**.
3. Select `models/pokedex-llama3-8b-q4.gguf`.
4. Start the local server (default port: `1234`).
5. Verify with: `curl http://localhost:1234/v1/models`

---

## Notes

- Do not commit `.gguf` files or `merged/` — they are large and reproducible from the training scripts.
- The `lora-adapter/` directory is also excluded; back it up externally if needed.
