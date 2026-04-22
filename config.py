"""
config.py

Load LM Studio connection settings from the environment or a .env file.
Override defaults by creating a .env file in the project root.

Example .env:
    LM_STUDIO_BASE_URL=http://localhost:1234/v1
    LM_STUDIO_MODEL=pokedex-llama3-8b-q4

Verified with LM Studio CLI v0.0.47 (`lms version`) on 2026-04-22.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

LM_STUDIO_BASE_URL: str = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
LM_STUDIO_MODEL: str = os.getenv("LM_STUDIO_MODEL", "pokedex-llama3-8b-q4")
LM_STUDIO_API_KEY: str = os.getenv("LM_STUDIO_API_KEY", "lm-studio")
