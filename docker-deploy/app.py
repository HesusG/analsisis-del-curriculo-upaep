"""Gradio entry point — Evaluador Curricular + RAG Chatbot + Delphi tabs."""

from __future__ import annotations

import os
from pathlib import Path

import gradio as gr

from config import LLM_MODEL
from evaluation.pipeline import run_evaluation_with_ingestion

# ── Lazy RAG chain (only built on first use) ──────────────────────────
_rag_chain = None
_APP_PASSWORD = os.getenv("APP_PASSWORD", "UPAEP2026")


def _get_rag_chain():
    global _rag_chain
    if _rag_chain is None:
        from rag.chain import build_rag_chain
        _rag_chain = build_rag_chain()
    return _rag_chain


def _invalidate_rag_chain():
    """Force RAG chain rebuild on next query so new docs are picked up."""
    global _rag_chain
    _rag_chain = None


# ── Pre-render Delphi tabs at startup (zero runtime cost) ────────────
def _build_delphi_html() -> tuple[str, str, str]:
    """Load Delphi data and render all 3 static tabs."""
    try:
        from delphi import load_delphi_data, render_delphi_summary, render_delphi_detail, render_metodologia
        data = load_delphi_data()
        return (
            render_delphi_summary(data),
            render_delphi_detail(data),
            render_metodologia(data),
        )
    except Exception as e:
        error_html = f"<p style='color:red;'>Error cargando datos Delphi: {e}</p>"
        return error_html, error_html, error_html


_delphi_summary_html, _delphi_detail_html, _metodologia_html = _build_delphi_html()


# ── Password gate ─────────────────────────────────────────────────────

def check_password(password: str):
    if password == _APP_PASSWORD:
        return (
            gr.update(visible=False),
            gr.update(visible=True),
            "",
        )
    return (
        gr.update(),
        gr.update(),
        "Contrasena incorrecta.",
    )


# ── Tab 1: Evaluation ──────────────────────────────────────────────────

async def run_evaluation_ui(pdf_filepath: str, progress=gr.Progress()):
    """Run 3-expert evaluation on uploaded PDF, return (summary_md, html_path)."""
    if pdf_filepath is None:
        return "Sube un archivo PDF para evaluar.", None

    progress(0.1, desc="Extrayendo texto del PDF...")

    try:
        progress(0.2, desc="Evaluando e indexando documento...")
        synthesis, html_path, ingest_result = await run_evaluation_with_ingestion(
            pdf_filepath
        )

        progress(0.9, desc="Generando reporte...")

        # Build summary
        lines = [
            "## Evaluacion completada",
            "",
            f"**Modelo:** {LLM_MODEL}",
            f"**Cumplimiento promedio:** {synthesis.average_compliance:.1f}%",
            f"**Nivel:** {synthesis.nivel_general.value}",
            "",
            "### Por experto:",
        ]
        for key, ev in synthesis.per_agent.items():
            lines.append(
                f"- **{ev.metadata.evaluador}**: "
                f"{ev.resumen_ejecutivo.porcentaje_cumplimiento:.1f}%"
            )

        # Per-section breakdown
        section_defs = [
            ("Datos", "parte_2_datos_presentacion"),
            ("Proposito", "parte_3_proposito_objetivo"),
            ("Contenidos", "parte_5_contenidos"),
            ("Metodologia", "parte_7_metodologia"),
            ("Evaluacion", "parte_8_evaluacion"),
        ]
        lines.extend(["", "### Desglose por seccion:"])
        for key, ev in synthesis.per_agent.items():
            parts_scores = []
            for label, attr in section_defs:
                criterios = getattr(ev, attr).criterios
                passed = sum(1 for c in criterios if c.cumple)
                total = len(criterios)
                parts_scores.append(f"{label}: {passed}/{total}")
            lines.append(
                f"- **{ev.metadata.evaluador}**: {' | '.join(parts_scores)}"
            )

        lines.extend(["", "### Fortalezas:"])
        for s in synthesis.strengths[:5]:
            lines.append(f"- {s}")

        lines.extend(["", "### Areas criticas:"])
        for a in synthesis.critical_areas[:5]:
            lines.append(f"- {a}")

        # Ingestion status
        lines.append("")
        if ingest_result.error:
            lines.append(
                f"*La indexacion fallo ({ingest_result.error}). "
                "La evaluacion se completo correctamente.*"
            )
        elif ingest_result.skipped_duplicate:
            lines.append("*Documento ya indexado previamente.*")
        elif ingest_result.success:
            _invalidate_rag_chain()
            lines.append(
                f"*Documento indexado ({ingest_result.chunks_added} fragmentos). "
                "Ya puedes consultarlo en 'Consultar Documentos'.*"
            )

        progress(1.0, desc="Listo.")
        return "\n".join(lines), html_path

    except Exception as e:
        return f"Error durante la evaluacion: {e}", None


# ── Tab 2: Panel de Expertos IA (Delphi Live) ────────────────────────

async def run_delphi_ui(pdf_filepath: str, progress=gr.Progress()):
    """Run 5-expert Delphi evaluation on uploaded PDF."""
    if pdf_filepath is None:
        return "Sube un archivo PDF para evaluar.", None, ""

    try:
        progress(0.05, desc="Extrayendo texto del PDF...")

        from delphi.live_pipeline import run_delphi_evaluation
        from delphi.live_agents import DELPHI_EXPERTS

        progress(0.10, desc="Dr. Critico evaluando...")

        result = await run_delphi_evaluation(pdf_filepath)

        progress(0.90, desc="Generando reporte...")

        # Build markdown summary
        lines = [
            "## Panel de Expertos IA completado",
            "",
            f"**Modelo:** {LLM_MODEL}",
            f"**Expertos:** {len(result.expert_evaluations)}",
            "",
            "### Scores por experto:",
        ]
        for key, ev in result.expert_evaluations.items():
            meta = result.expert_metas[key]
            scores = [p.score for p in ev.puntuaciones]
            avg = sum(scores) / len(scores) if scores else 0
            lines.append(f"- **{meta.name}**: {avg:.1f}/10")

        if result.synthesis:
            # Consolidated scores
            lines.extend(["", "### Scores consolidados:"])
            for p in result.synthesis.puntuaciones_consolidadas:
                lines.append(f"- **{p.dimension}**: {p.score}/10")

            # Top recommendations
            alta = [r for r in result.synthesis.recomendaciones_priorizadas if r.prioridad == "Alta"]
            if alta:
                lines.extend(["", "### Recomendaciones de alta prioridad:"])
                for r in alta[:5]:
                    lines.append(f"- {r.texto}")

        progress(1.0, desc="Listo.")

        # Read HTML for inline display
        html_content = ""
        if result.html_path:
            from pathlib import Path as P
            html_content = P(result.html_path).read_text(encoding="utf-8")

        return "\n".join(lines), result.html_path, html_content

    except Exception as e:
        import traceback
        return f"Error durante la evaluacion Delphi: {e}\n\n```\n{traceback.format_exc()}\n```", None, ""


# ── Tab 3: RAG Chat ───────────────────────────────────────────────────

def chat_respond(user_message: str, chatbot_history: list, chain_history: list):
    """Invoke RAG chain and return updated chatbot + state."""
    if not user_message.strip():
        return chatbot_history, chain_history, ""

    try:
        chain = _get_rag_chain()
    except Exception as e:
        error_msg = f"Error conectando a ChromaDB: {e}"
        chatbot_history.append({"role": "user", "content": user_message})
        chatbot_history.append({"role": "assistant", "content": error_msg})
        return chatbot_history, chain_history, ""

    result = chain.invoke(
        {"question": user_message, "chat_history": chain_history}
    )

    answer = result["answer"]
    source_docs = result.get("source_documents", [])

    # Append sources
    if source_docs:
        sources_text = "\n\n---\n**Fuentes:**\n"
        seen = set()
        for doc in source_docs:
            source = doc.metadata.get("source", "desconocido")
            if source not in seen:
                seen.add(source)
                sources_text += f"- `{Path(source).name}`\n"
        answer += sources_text

    # Update histories
    chatbot_history.append({"role": "user", "content": user_message})
    chatbot_history.append({"role": "assistant", "content": answer})
    chain_history.append((user_message, answer))

    return chatbot_history, chain_history, ""


# ── Gradio UI ──────────────────────────────────────────────────────────

theme = gr.themes.Default(primary_hue="red")

with gr.Blocks(theme=theme, title="Evaluador Curricular UPAEP") as demo:

    # ── Login screen ──
    with gr.Column(visible=True) as login_col:
        gr.Markdown("# Evaluador Curricular UPAEP")
        gr.Markdown("Ingresa la contrasena para acceder.")
        pwd_input = gr.Textbox(
            label="Contrasena",
            type="password",
            placeholder="Contrasena...",
        )
        login_btn = gr.Button("Entrar", variant="primary")
        login_msg = gr.Markdown("")

    # ── Main app (hidden until login) ──
    with gr.Column(visible=False) as main_col:
        gr.Markdown("# Evaluador Curricular UPAEP")
        gr.Markdown(
            f"Evalua planeaciones didacticas con IA ({LLM_MODEL}) "
            "o consulta los documentos curriculares."
        )

        with gr.Tab("Evaluar Planeacion"):
            gr.Markdown("*Solo se aceptan archivos PDF por el momento.*")
            pdf_input = gr.File(
                label="Sube la planeacion en PDF",
                file_types=[".pdf"],
                type="filepath",
            )
            eval_btn = gr.Button("Evaluar", variant="primary")
            eval_output = gr.Markdown(label="Resultado")
            report_file = gr.File(
                label="Reporte HTML descargable",
                interactive=False,
            )

            eval_btn.click(
                fn=run_evaluation_ui,
                inputs=[pdf_input],
                outputs=[eval_output, report_file],
            )

        with gr.Tab("Panel de Expertos IA"):
            gr.Markdown(
                "Evaluacion Delphi con 5 expertos IA. "
                "Cada experto evalua desde su marco teorico en 6 dimensiones (1-10)."
            )
            delphi_pdf_input = gr.File(
                label="Sube la planeacion en PDF",
                file_types=[".pdf"],
                type="filepath",
            )
            delphi_btn = gr.Button("Evaluar con 5 expertos", variant="primary")
            delphi_output = gr.Markdown(label="Resultado")
            delphi_report_file = gr.File(
                label="Reporte HTML descargable",
                interactive=False,
            )
            delphi_html_display = gr.HTML(label="Reporte")

            delphi_btn.click(
                fn=run_delphi_ui,
                inputs=[delphi_pdf_input],
                outputs=[delphi_output, delphi_report_file, delphi_html_display],
            )

        with gr.Tab("Consultar Documentos"):
            chatbot = gr.Chatbot(type="messages", label="Chat RAG")
            chain_state = gr.State([])
            user_input = gr.Textbox(
                placeholder="Pregunta sobre los documentos curriculares...",
                label="Tu pregunta",
                lines=1,
            )
            send_btn = gr.Button("Enviar", variant="primary")

            send_btn.click(
                fn=chat_respond,
                inputs=[user_input, chatbot, chain_state],
                outputs=[chatbot, chain_state, user_input],
            )
            user_input.submit(
                fn=chat_respond,
                inputs=[user_input, chatbot, chain_state],
                outputs=[chatbot, chain_state, user_input],
            )

        with gr.Tab("Delphi: Resumen"):
            gr.HTML(_delphi_summary_html)

        with gr.Tab("Delphi: Detalle"):
            gr.HTML(_delphi_detail_html)

        with gr.Tab("Metodologia"):
            gr.HTML(_metodologia_html)

    # ── Wire login ──
    login_btn.click(
        fn=check_password,
        inputs=[pwd_input],
        outputs=[login_col, main_col, login_msg],
    )
    pwd_input.submit(
        fn=check_password,
        inputs=[pwd_input],
        outputs=[login_col, main_col, login_msg],
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
