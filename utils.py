"""
utils.py

Shared helpers for the Gradio inference app.
"""

import re
import subprocess
import time

import httpx
from openai import OpenAI

FALLBACK = "(not generated)"

SYSTEM_PROMPT = (
    "You are a Pokédex from the original Game Boy games. "
    "Given a description, generate a Pokémon name, type(s), and a brief Pokédex entry. "
    "Use terse, biological, slightly ominous language — one or two sentences maximum. "
    "Always respond using exactly this format:\n"
    "[Name]: <name>\n"
    "[Type]: <type or types>\n"
    "[Entry]: <entry text>"
)


def build_prompt(description: str) -> str:
    """Return the DEC-004 formatted user message for the given description."""
    return (
        f"[Description]: {description.strip()}\n"
        "[Name]:\n"
        "[Type]:\n"
        "[Entry]:"
    )


def parse_completion(text: str) -> tuple[str, str, str]:
    """
    Extract [Name], [Type], and [Entry] fields from a model completion.

    Returns a (name, type_, entry) tuple. Any missing field is replaced with
    FALLBACK so the caller never receives an empty string.
    """
    def extract(label: str) -> str:
        pattern = rf"\[{label}\]:\s*(.+?)(?=\n\[|\Z)"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            value = match.group(1).strip()
            return value if value else FALLBACK
        return FALLBACK

    return extract("Name"), extract("Type"), extract("Entry")


# ---------------------------------------------------------------------------
# LM Studio server management
# ---------------------------------------------------------------------------

_POLL_INTERVAL = 2  # seconds between readiness checks
_MAX_WAIT = 30      # seconds before giving up after a start attempt


def _server_is_up(base_url: str) -> bool:
    """Return True if the LM Studio API responds on the /models endpoint."""
    try:
        r = httpx.get(f"{base_url.rstrip('/')}/models", timeout=3.0)
        return r.status_code == 200
    except httpx.TransportError:
        return False


def ensure_server_running(base_url: str) -> None:
    """
    Ensure the LM Studio server is accepting connections.

    If the server is already up, returns immediately. Otherwise, attempts to
    start it via the `lms server start` CLI command and waits up to
    _MAX_WAIT seconds for it to become ready.

    Raises RuntimeError if the server does not become ready in time.
    """
    if _server_is_up(base_url):
        print("LM Studio server is already running.")
        return

    print("LM Studio server not detected — attempting to start via 'lms server start'...")
    try:
        subprocess.Popen(
            ["lms", "server", "start"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "'lms' CLI not found. Ensure LM Studio is installed and 'lms' is on your PATH. "
            "You can also start the LM Studio server manually before running this app."
        ) from exc

    deadline = time.monotonic() + _MAX_WAIT
    while time.monotonic() < deadline:
        time.sleep(_POLL_INTERVAL)
        if _server_is_up(base_url):
            print("LM Studio server is ready.")
            return

    raise RuntimeError(
        f"LM Studio server did not become ready within {_MAX_WAIT} seconds. "
        "Check that a model is loaded in LM Studio and the server is enabled."
    )


def list_models(client: OpenAI) -> list[str]:
    """Return the list of model IDs currently available in LM Studio."""
    models = client.models.list()
    return [m.id for m in models.data]
