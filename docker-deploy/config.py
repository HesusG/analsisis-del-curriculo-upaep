"""Configuration constants for the evaluator app (HF Spaces / Cloud deployment)."""

import os
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────
APP_DIR = Path(__file__).resolve().parent

# Conditional dotenv (only for local dev; HF Spaces uses env vars directly)
try:
    from dotenv import load_dotenv

    env_path = APP_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

# Agent system prompts (bundled in data/)
AGENT_PROMPTS_DIR = APP_DIR / "data" / "agentes"
RULES_PATH = APP_DIR / "data" / "analisis_planeacion" / "rules.md"

# Output (writable in containers)
OUTPUT_DIR = Path("/tmp/evaluator_output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── ChromaDB Cloud ─────────────────────────────────────────────────────
CHROMA_API_KEY = os.environ.get("CHROMA_API_KEY", "")
CHROMA_TENANT = os.environ.get("CHROMA_TENANT", "")
CHROMA_DATABASE = os.environ.get("CHROMA_DATABASE", "")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "curriculo-upaep")

# ── LLM Settings ───────────────────────────────────────────────────────
LLM_MODEL = "gpt-4o"
LLM_TEMPERATURE = 0.2
EMBEDDING_MODEL = "text-embedding-3-small"

# ── RAG Settings ───────────────────────────────────────────────────────
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
RETRIEVER_K = 4
RAG_TEMPERATURE = 0.3

# ── Agent Metadata ─────────────────────────────────────────────────────
AGENT_META = {
    "pedagogo": {
        "name": "Pedagogo",
        "color": "#BA68C8",
        "emoji": "\U0001F4DA",
        "description": "Experto en teoría curricular y pedagogía crítica",
        "prompt_file": "evaluador-pedagogo.md",
    },
    "profesor": {
        "name": "Profesor",
        "color": "#64B5F6",
        "emoji": "\U0001F9D1\u200D\U0001F3EB",
        "description": "Simula la evaluación con la rúbrica de la Dra. Mendoza",
        "prompt_file": "evaluador-profesor.md",
    },
    "tecnico": {
        "name": "Técnico",
        "color": "#81C784",
        "emoji": "\U0001F4CB",
        "description": "Especialista en formato APA 7 y estructura documental",
        "prompt_file": "evaluador-tecnico.md",
    },
}
