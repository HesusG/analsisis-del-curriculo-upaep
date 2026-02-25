"""Configuration constants for the evaluator app."""

from pathlib import Path
from dotenv import load_dotenv

# ── Paths ──────────────────────────────────────────────────────────────
APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent

# Load .env from simulation/ (shared API keys)
ENV_PATH = PROJECT_ROOT / "simulation" / ".env"
load_dotenv(ENV_PATH)

# Agent system prompts
AGENT_PROMPTS_DIR = PROJECT_ROOT / "agentes"
RULES_PATH = PROJECT_ROOT / "analisis_planeacion" / "rules.md"

# Sources for RAG
SOURCES_DIR = PROJECT_ROOT / "sources"

# Output
OUTPUT_DIR = APP_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ChromaDB persistence
CHROMA_DIR = APP_DIR / ".chroma_db"

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
