"""
app.py

Phase 3 — Gradio inference interface for the fine-tuned Pokédex model.

Usage:
    python app.py

Requires:
    - LM Studio running locally with the GGUF model loaded and the server enabled.
    - config.py (or a .env file) with LM_STUDIO_BASE_URL and LM_STUDIO_MODEL set.

Environment variables (can also be set in .env):
    LM_STUDIO_BASE_URL   — LM Studio API base URL (default: http://localhost:1234/v1)
    LM_STUDIO_MODEL      — Model name as shown in LM Studio (default: pokedex-llama3-8b-q4)
"""

import gradio as gr
from openai import OpenAI, OpenAIError

from config import LM_STUDIO_API_KEY, LM_STUDIO_BASE_URL, LM_STUDIO_MODEL
from utils import FALLBACK, SYSTEM_PROMPT, build_prompt, ensure_server_running, list_models, parse_completion

client = OpenAI(base_url=LM_STUDIO_BASE_URL, api_key=LM_STUDIO_API_KEY)


def generate(description: str) -> tuple[str, str, str]:
    """Call LM Studio and return (name, type_, entry) for the given description."""
    description = description.strip()
    if not description:
        return FALLBACK, FALLBACK, FALLBACK

    try:
        response = client.chat.completions.create(
            model=LM_STUDIO_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_prompt(description)},
            ],
            temperature=0.8,
            max_tokens=128,
        )
        raw = response.choices[0].message.content or ""
    except OpenAIError as exc:
        error_msg = f"API error: {exc}"
        return error_msg, FALLBACK, FALLBACK

    return parse_completion(raw)


with gr.Blocks(title="Pokédex Generator") as demo:
    gr.Markdown("# Pokédex Generator\nDescribe a Pokémon and the model will name it, type it, and write its entry.")

    with gr.Row():
        description_input = gr.Textbox(
            label="Describe your Pokémon",
            placeholder="e.g. A tiny ghost that lives in old clocks",
            lines=2,
        )

    generate_btn = gr.Button("Generate", variant="primary")

    with gr.Row():
        name_output = gr.Textbox(label="Name", interactive=False)
        type_output = gr.Textbox(label="Type(s)", interactive=False)

    entry_output = gr.Textbox(label="Pokédex Entry", interactive=False, lines=3)

    generate_btn.click(
        fn=generate,
        inputs=description_input,
        outputs=[name_output, type_output, entry_output],
    )

    description_input.submit(
        fn=generate,
        inputs=description_input,
        outputs=[name_output, type_output, entry_output],
    )


if __name__ == "__main__":
    ensure_server_running(LM_STUDIO_BASE_URL)
    available = list_models(client)
    print(f"Available models: {available}")
    demo.launch()
