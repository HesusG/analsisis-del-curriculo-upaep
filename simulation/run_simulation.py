#!/usr/bin/env python3
"""
Simulación Wideband Delphi - Juicio de Expertos Curriculares
Evalúa el currículum MT1001B usando 4 agentes LLM con perspectivas teóricas diversas.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from together import Together
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Cargar variables de entorno
load_dotenv()

console = Console()

# Configuración de modelos
TOGETHER_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
QWEN_MODEL = "Qwen/Qwen2.5-72B-Instruct-Turbo"  # Modelo alternativo
OPENAI_MODEL = "gpt-4o"

# Directorio base
BASE_DIR = Path(__file__).parent
PROMPTS_DIR = BASE_DIR / "prompts"
OUTPUT_DIR = BASE_DIR / "output"
SOURCES_DIR = BASE_DIR.parent / "sources"

# Crear directorio de output si no existe
OUTPUT_DIR.mkdir(exist_ok=True)


def load_prompt(filename: str) -> str:
    """Carga un system prompt desde archivo."""
    with open(PROMPTS_DIR / filename, "r", encoding="utf-8") as f:
        return f.read()


def load_curriculum() -> str:
    """Carga toda la documentación del currículum desde sources/."""
    curriculum_parts = []

    files_to_load = [
        "organizacion_curso.md",
        "competencias.md",
        "secuencia_didactica.md",
        "perfil_ingreso.md",
        "objetivos_aprendizaje.md"
    ]

    for filename in files_to_load:
        filepath = SOURCES_DIR / filename
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                curriculum_parts.append(f"## {filename}\n\n{content}")

    return "\n\n---\n\n".join(curriculum_parts)


class ExpertAgent:
    """Agente experto usando Together AI."""

    def __init__(self, name: str, prompt_file: str, model: str = None):
        self.name = name
        self.system_prompt = load_prompt(prompt_file)
        self.client = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        self.model = model or TOGETHER_MODEL
        self.history = []

    def evaluate(self, curriculum: str, additional_context: str = "") -> str:
        """Evalúa el currículum según la perspectiva del experto."""
        user_message = f"""Analiza el siguiente currículum del curso MT1001B del Tecnológico de Monterrey:

{curriculum}

{additional_context}

Proporciona tu evaluación completa siguiendo el formato especificado en tus instrucciones."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=2000,
            temperature=0.7
        )

        result = response.choices[0].message.content
        self.history.append({"round": len(self.history) + 1, "response": result})
        return result


class Moderator:
    """Moderador usando OpenAI GPT-4o."""

    def __init__(self):
        self.system_prompt = load_prompt("moderador_system.md")
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def synthesize(self, expert_responses: dict, round_num: int) -> str:
        """Sintetiza las respuestas de los expertos."""

        responses_text = "\n\n".join([
            f"### {name}\n{response}"
            for name, response in expert_responses.items()
        ])

        if round_num == 3:
            user_message = f"""Es la Ronda 3 (final) del proceso Delphi.

Aquí están todas las evaluaciones y debates de los expertos:

{responses_text}

Genera el REPORTE FINAL completo según el formato especificado, incluyendo:
- Resumen ejecutivo
- Consensos alcanzados
- Disensos fundamentados
- Tabla de puntuaciones consolidadas
- Recomendaciones priorizadas
- Conclusiones del panel"""
        else:
            user_message = f"""Ronda {round_num} del proceso Delphi.

Respuestas de los expertos:

{responses_text}

Resume las posiciones de cada experto para facilitar el debate en la siguiente ronda."""

        response = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=4000,
            temperature=0.5
        )

        return response.choices[0].message.content


def run_delphi_simulation():
    """Ejecuta la simulación completa del Wideband Delphi."""

    console.print(Panel.fit(
        "[bold blue]Simulación Wideband Delphi[/bold blue]\n"
        "Juicio de Expertos sobre Currículum MT1001B",
        border_style="blue"
    ))

    # Cargar currículum
    console.print("\n[yellow]Cargando documentación del currículum...[/yellow]")
    curriculum = load_curriculum()
    console.print(f"[green]✓ Currículum cargado ({len(curriculum)} caracteres)[/green]")

    # Inicializar agentes
    console.print("\n[yellow]Inicializando panel de expertos...[/yellow]")

    experts = {
        "Dr. Crítico": ExpertAgent("Dr. Crítico", "critico_system.md"),
        "Dra. Multiliteracidades": ExpertAgent("Dra. Multiliteracidades", "multiliteracidades_system.md"),
        "Dr. Conectivista": ExpertAgent("Dr. Conectivista", "conectivista_system.md"),
        "Dra. Marketing Educativo": ExpertAgent("Dra. Marketing Educativo", "marketing_system.md"),
        # Experto adicional usando Qwen (modelo alternativo)
        "Dr. Pedagogía Crítica": ExpertAgent("Dr. Pedagogía Crítica", "pedagogia_critica_system.md", model=QWEN_MODEL),
    }

    moderator = Moderator()
    console.print("[green]✓ Panel inicializado (5 expertos + 1 moderador)[/green]")

    all_responses = {}

    # === RONDA 1: Evaluación Individual ===
    console.print("\n" + "="*60)
    console.print("[bold cyan]RONDA 1: Evaluación Individual[/bold cyan]")
    console.print("="*60)

    round1_responses = {}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        for name, expert in experts.items():
            task = progress.add_task(f"[cyan]{name} evaluando...", total=None)
            response = expert.evaluate(curriculum)
            round1_responses[name] = response
            progress.update(task, completed=True, description=f"[green]✓ {name} completado")

            # Guardar respuesta individual
            output_file = OUTPUT_DIR / f"ronda1_{name.lower().replace(' ', '_').replace('.', '')}.md"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# {name} - Ronda 1\n\n{response}")

    all_responses["ronda1"] = round1_responses

    # Resumen del moderador para Ronda 1
    console.print("\n[yellow]Moderador sintetizando Ronda 1...[/yellow]")
    round1_summary = moderator.synthesize(round1_responses, 1)

    with open(OUTPUT_DIR / "ronda1_resumen.md", "w", encoding="utf-8") as f:
        f.write(f"# Resumen Ronda 1\n\n{round1_summary}")

    console.print("[green]✓ Ronda 1 completada[/green]")

    # === RONDA 2: Debate y Confrontación ===
    console.print("\n" + "="*60)
    console.print("[bold cyan]RONDA 2: Debate y Confrontación[/bold cyan]")
    console.print("="*60)

    round2_responses = {}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        for name, expert in experts.items():
            # Preparar contexto con opiniones de otros
            other_opinions = "\n\n".join([
                f"**{other_name}**: {other_response[:500]}..."
                for other_name, other_response in round1_responses.items()
                if other_name != name
            ])

            debate_context = f"""
## Resumen de la Ronda 1 (por el moderador):
{round1_summary}

## Posiciones de los otros expertos:
{other_opinions}

## Tu evaluación previa:
{round1_responses[name][:500]}...

---

Ahora, considerando las perspectivas de tus colegas:
1. ¿En qué puntos COINCIDES con ellos y por qué?
2. ¿En qué puntos DISIENTES y cuáles son tus argumentos?
3. ¿Modificas alguna de tus puntuaciones? Justifica.
4. ¿Qué nuevas reflexiones surgen del diálogo?
"""

            task = progress.add_task(f"[cyan]{name} debatiendo...", total=None)
            response = expert.evaluate(curriculum, debate_context)
            round2_responses[name] = response
            progress.update(task, completed=True, description=f"[green]✓ {name} completado")

            # Guardar respuesta
            output_file = OUTPUT_DIR / f"ronda2_{name.lower().replace(' ', '_').replace('.', '')}.md"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# {name} - Ronda 2 (Debate)\n\n{response}")

    all_responses["ronda2"] = round2_responses

    # Resumen del moderador para Ronda 2
    console.print("\n[yellow]Moderador sintetizando Ronda 2...[/yellow]")
    round2_summary = moderator.synthesize(round2_responses, 2)

    with open(OUTPUT_DIR / "ronda2_resumen.md", "w", encoding="utf-8") as f:
        f.write(f"# Resumen Ronda 2\n\n{round2_summary}")

    console.print("[green]✓ Ronda 2 completada[/green]")

    # === RONDA 3: Convergencia y Consenso ===
    console.print("\n" + "="*60)
    console.print("[bold cyan]RONDA 3: Convergencia y Consenso Final[/bold cyan]")
    console.print("="*60)

    # Combinar todo para el reporte final
    all_expert_input = {}
    for name in experts.keys():
        all_expert_input[name] = f"""
### Ronda 1 (Evaluación inicial):
{round1_responses[name]}

### Ronda 2 (Debate):
{round2_responses[name]}
"""

    console.print("\n[yellow]Moderador generando reporte final...[/yellow]")
    final_report = moderator.synthesize(all_expert_input, 3)

    # Guardar reporte final
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_file = OUTPUT_DIR / f"reporte_final_{timestamp}.md"

    with open(final_file, "w", encoding="utf-8") as f:
        f.write(final_report)

    # También guardar como reporte_final.md (última versión)
    with open(OUTPUT_DIR / "reporte_final.md", "w", encoding="utf-8") as f:
        f.write(final_report)

    console.print(f"[green]✓ Reporte final guardado en: {final_file}[/green]")

    # Mostrar resumen en consola
    console.print("\n" + "="*60)
    console.print(Panel.fit(
        "[bold green]Simulación Completada[/bold green]\n\n"
        f"Archivos generados en: {OUTPUT_DIR}\n"
        "- ronda1_*.md (evaluaciones individuales)\n"
        "- ronda2_*.md (debates)\n"
        "- reporte_final.md (síntesis completa)",
        border_style="green"
    ))

    return final_report


if __name__ == "__main__":
    try:
        # Verificar API keys
        if not os.getenv("TOGETHER_API_KEY"):
            console.print("[red]Error: TOGETHER_API_KEY no configurada en .env[/red]")
            exit(1)
        if not os.getenv("OPENAI_API_KEY"):
            console.print("[red]Error: OPENAI_API_KEY no configurada en .env[/red]")
            exit(1)

        # Ejecutar simulación
        report = run_delphi_simulation()

        # Mostrar primeras líneas del reporte
        console.print("\n[bold]Primeras líneas del reporte:[/bold]")
        console.print(report[:1000] + "...")

    except Exception as e:
        console.print(f"[red]Error durante la simulación: {e}[/red]")
        raise
