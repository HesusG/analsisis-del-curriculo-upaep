"""Load and parse Wideband Delphi simulation .md files at startup."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import markdown

DELPHI_DIR = Path(__file__).parent
DATA_DIR = DELPHI_DIR / "data"
PROMPTS_DIR = DELPHI_DIR / "prompts"

_MD = markdown.Markdown(extensions=["tables", "fenced_code"])


def _md_to_html(text: str) -> str:
    """Convert markdown text to HTML, resetting the converter each time."""
    _MD.reset()
    return _MD.convert(text)


def _read(path: Path) -> str:
    """Read a file, stripping outer markdown fences if present."""
    text = path.read_text(encoding="utf-8")
    # Some files wrap content in ```markdown ... ```
    stripped = text.strip()
    if stripped.startswith("```markdown") or stripped.startswith("```md"):
        lines = stripped.split("\n")
        # Remove first and last fence lines
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return text


@dataclass
class ExpertInfo:
    name: str
    framework: str
    model: str
    prompt_html: str


@dataclass
class DelphiData:
    """All pre-loaded Delphi content as HTML fragments."""
    # Expert panel
    experts: list[ExpertInfo] = field(default_factory=list)
    # Ronda 1
    ronda1_experts: dict[str, str] = field(default_factory=dict)  # name → html
    ronda1_summary: str = ""
    # Ronda 2
    ronda2_experts: dict[str, str] = field(default_factory=dict)  # name → html
    ronda2_summary: str = ""
    # Final report
    reporte_final: str = ""
    # Moderator prompt
    moderador_prompt: str = ""


# Expert definitions matching the local simulation
EXPERT_DEFS = [
    ("Dr. Crítico", "Teoría curricular crítica (Apple, Gimeno Sacristán)", "Llama 3.3 70B",
     "critico_system.md", "ronda1_dr_crítico.md", "ronda2_dr_crítico.md"),
    ("Dra. Multiliteracidades", "Pedagogía del nuevo aprendizaje (Cope & Kalantzis)", "Qwen 2.5 72B",
     "multiliteracidades_system.md", "ronda1_dra_multiliteracidades.md", "ronda2_dra_multiliteracidades.md"),
    ("Dr. Conectivista", "Aprendizaje en era digital (Siemens)", "GPT-4o",
     "conectivista_system.md", "ronda1_dr_conectivista.md", "ronda2_dr_conectivista.md"),
    ("Dra. Marketing Educativo", "Innovación en educación de negocios (Guha, Demirci)", "Llama 3.3 70B",
     "marketing_system.md", "ronda1_dra_marketing_educativo.md", "ronda2_dra_marketing_educativo.md"),
    ("Dr. Pedagogía Crítica", "Pedagogía de la liberación (Freire, Giroux)", "Qwen 2.5 72B",
     "pedagogia_critica_system.md", "ronda1_dr_pedagogía_crítica.md", "ronda2_dr_pedagogía_crítica.md"),
]


def load_delphi_data() -> DelphiData:
    """Load all Delphi files and convert to HTML. Called once at startup."""
    data = DelphiData()

    for name, framework, model, prompt_file, r1_file, r2_file in EXPERT_DEFS:
        # Prompt
        prompt_path = PROMPTS_DIR / prompt_file
        prompt_html = _md_to_html(_read(prompt_path)) if prompt_path.exists() else ""

        data.experts.append(ExpertInfo(
            name=name,
            framework=framework,
            model=model,
            prompt_html=prompt_html,
        ))

        # Ronda 1
        r1_path = DATA_DIR / r1_file
        if r1_path.exists():
            data.ronda1_experts[name] = _md_to_html(_read(r1_path))

        # Ronda 2
        r2_path = DATA_DIR / r2_file
        if r2_path.exists():
            data.ronda2_experts[name] = _md_to_html(_read(r2_path))

    # Summaries
    r1_summary = DATA_DIR / "ronda1_resumen.md"
    if r1_summary.exists():
        data.ronda1_summary = _md_to_html(_read(r1_summary))

    r2_summary = DATA_DIR / "ronda2_resumen.md"
    if r2_summary.exists():
        data.ronda2_summary = _md_to_html(_read(r2_summary))

    # Final report
    reporte = DATA_DIR / "reporte_final.md"
    if reporte.exists():
        data.reporte_final = _md_to_html(_read(reporte))

    # Moderator
    mod = PROMPTS_DIR / "moderador_system.md"
    if mod.exists():
        data.moderador_prompt = _md_to_html(_read(mod))

    return data
