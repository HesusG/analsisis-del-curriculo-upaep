"""Gradio entry point — Evaluador Curricular + RAG Chatbot + Como funciona."""

from __future__ import annotations

import os
from pathlib import Path

import gradio as gr

from config import DAILY_EVAL_LIMIT, LLM_MODEL_DISPLAY
from evaluation.pipeline import run_evaluation_with_ingestion
from history.db import HistoryDB
from history.helpers import summarize_3expert, summarize_delphi

# ── Lazy RAG chain (only built on first use) ──────────────────────────
_rag_chain = None
_APP_PASSWORD = os.getenv("APP_PASSWORD", "UPAEP2026")
_history_db = HistoryDB()


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


# ── ChromaDB connection diagnostic ───────────────────────────────────

def _check_chroma_connection():
    """Log ChromaDB connection status at startup."""
    from config import CHROMA_API_KEY, CHROMA_TENANT, CHROMA_DATABASE
    if not all([CHROMA_API_KEY, CHROMA_TENANT, CHROMA_DATABASE]):
        missing = []
        if not CHROMA_API_KEY:
            missing.append("CHROMA_API_KEY")
        if not CHROMA_TENANT:
            missing.append("CHROMA_TENANT")
        if not CHROMA_DATABASE:
            missing.append("CHROMA_DATABASE")
        print(f"[ChromaDB] Credentials missing ({', '.join(missing)}) — RAG disabled")
        return
    try:
        import chromadb
        client = chromadb.CloudClient(
            tenant=CHROMA_TENANT,
            database=CHROMA_DATABASE,
            api_key=CHROMA_API_KEY,
        )
        client.heartbeat()
        print("[ChromaDB] Connected OK")
    except Exception as e:
        print(f"[ChromaDB] Connection failed: {e}")


_check_chroma_connection()


# ── Rate limit display ────────────────────────────────────────────────

def _get_usage_display() -> str:
    """Return HTML progress bar showing daily evaluation usage."""
    used = _history_db.count_today()
    limit = DAILY_EVAL_LIMIT
    pct = min(int(used / limit * 100), 100) if limit > 0 else 100

    if used >= limit:
        return (
            '<div style="background:#991B1B;border-radius:8px;height:28px;margin:8px 0;'
            'display:flex;align-items:center;justify-content:center;color:white;'
            'font-size:13px;font-weight:600">'
            f'Limite diario alcanzado ({used}/{limit}). Vuelve manana.'
            '</div>'
        )
    return (
        '<div style="background:#e5e7eb;border-radius:8px;overflow:hidden;height:28px;margin:8px 0">'
        f'<div style="background:#DC2626;height:100%;width:{pct}%;min-width:fit-content;'
        'transition:width 0.3s;display:flex;align-items:center;padding:0 10px;'
        'color:white;font-size:13px;font-weight:500">'
        f'{used}/{limit} evaluaciones hoy'
        '</div></div>'
    )


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


# ── Unified evaluation callback ──────────────────────────────────────

async def _run_unified_eval(pdf_filepath: str, mode: str, progress=gr.Progress()):
    """Dispatch to 3-expert or 5-expert evaluation based on mode radio."""
    if mode == "5 Expertos (Delphi)":
        return await _run_delphi(pdf_filepath, progress)
    return await _run_3expert(pdf_filepath, progress)


async def _run_3expert(pdf_filepath: str, progress=gr.Progress()):
    """Run 3-expert evaluation, return (summary_md, html_path, html_inline, usage_html)."""
    if pdf_filepath is None:
        return "Sube un archivo PDF para evaluar.", None, "", _get_usage_display()

    if _history_db.count_today() >= DAILY_EVAL_LIMIT:
        return "**Limite diario alcanzado.** Vuelve manana.", None, "", _get_usage_display()

    progress(0.1, desc="Extrayendo texto del PDF...")

    try:
        progress(0.2, desc="Evaluando e indexando documento...")
        synthesis, html_path, ingest_result = await run_evaluation_with_ingestion(
            pdf_filepath
        )

        progress(0.9, desc="Generando reporte...")

        # Save to history
        try:
            _history_db.save_evaluation(
                pdf_name=Path(pdf_filepath).stem,
                eval_type="evaluacion",
                score=synthesis.average_compliance,
                nivel_general=synthesis.nivel_general.value,
                per_agent_summary=summarize_3expert(synthesis),
                html_report_path=html_path or "",
            )
        except Exception:
            pass

        # ── Lean markdown summary ──
        lines = [
            f"# {synthesis.average_compliance:.1f}% Cumplimiento — {synthesis.nivel_general.value}",
            "",
            "| Experto | Score |",
            "|---------|-------|",
        ]
        for key, ev in synthesis.per_agent.items():
            lines.append(
                f"| {ev.metadata.evaluador} | {ev.resumen_ejecutivo.porcentaje_cumplimiento:.1f}% |"
            )

        # Consensus
        if synthesis.consensus:
            n_consensus = len(synthesis.consensus)
            lines.extend(["", f"### Consensos clave ({n_consensus} criterios)"])
            for cr in synthesis.consensus:
                passed = list(cr.votes.values())[0]
                icon = "+" if passed else "-"
                lines.append(f"- [{icon}] {cr.criterio}")

        # Critical areas
        if synthesis.critical_areas:
            lines.extend(["", "### Areas criticas"])
            for a in synthesis.critical_areas[:5]:
                lines.append(f"- {a}")

        lines.extend(["", "*Descarga el reporte HTML para ver el detalle completo.*"])

        # Handle RAG indexation silently
        if ingest_result.success and not ingest_result.skipped_duplicate:
            _invalidate_rag_chain()

        # Read HTML for inline display
        html_content = ""
        if html_path:
            html_content = Path(html_path).read_text(encoding="utf-8")

        progress(1.0, desc="Listo.")
        return "\n".join(lines), html_path, html_content, _get_usage_display()

    except Exception as e:
        return f"Error durante la evaluacion: {e}", None, "", _get_usage_display()


async def _run_delphi(pdf_filepath: str, progress=gr.Progress()):
    """Run 5-expert Delphi evaluation, return (summary_md, html_path, html_inline, usage_html)."""
    if pdf_filepath is None:
        return "Sube un archivo PDF para evaluar.", None, "", _get_usage_display()

    if _history_db.count_today() >= DAILY_EVAL_LIMIT:
        return "**Limite diario alcanzado.** Vuelve manana.", None, "", _get_usage_display()

    try:
        progress(0.05, desc="Extrayendo texto del PDF...")

        from delphi.live_pipeline import run_delphi_evaluation

        progress(0.10, desc="Expertos evaluando...")

        result = await run_delphi_evaluation(pdf_filepath)

        progress(0.90, desc="Generando reporte...")

        # Save to history
        try:
            all_scores = []
            for ev in result.expert_evaluations.values():
                for p in ev.puntuaciones:
                    all_scores.append(p.score)
            avg_score = sum(all_scores) / len(all_scores) if all_scores else 0.0

            _history_db.save_evaluation(
                pdf_name=result.pdf_name or Path(pdf_filepath).stem,
                eval_type="delphi",
                score=avg_score,
                nivel_general="",
                per_agent_summary=summarize_delphi(result),
                html_report_path=result.html_path or "",
            )
        except Exception:
            pass

        # ── Lean markdown summary ──
        expert_scores = []
        for key, ev in result.expert_evaluations.items():
            meta = result.expert_metas[key]
            scores = [p.score for p in ev.puntuaciones]
            avg = sum(scores) / len(scores) if scores else 0
            expert_scores.append((meta.name, avg))

        overall_avg = sum(s for _, s in expert_scores) / len(expert_scores) if expert_scores else 0

        lines = [
            f"# {overall_avg:.1f}/10 Score Promedio",
            "",
            "| Experto | Score |",
            "|---------|-------|",
        ]
        for name, score in expert_scores:
            lines.append(f"| {name} | {score:.1f}/10 |")

        if result.synthesis:
            alta = [r for r in result.synthesis.recomendaciones_priorizadas if r.prioridad == "Alta"]
            if alta:
                lines.extend(["", "### Recomendaciones de alta prioridad"])
                for r in alta[:5]:
                    lines.append(f"- {r.texto}")

        lines.extend(["", "*Descarga el reporte HTML para ver el detalle completo.*"])

        progress(1.0, desc="Listo.")

        # Read HTML for inline display
        html_content = ""
        if result.html_path:
            html_content = Path(result.html_path).read_text(encoding="utf-8")

        return "\n".join(lines), result.html_path, html_content, _get_usage_display()

    except Exception as e:
        import traceback
        return f"Error durante la evaluacion Delphi: {e}\n\n```\n{traceback.format_exc()}\n```", None, "", _get_usage_display()


# ── RAG Chat ─────────────────────────────────────────────────────────

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


# ── Historial ────────────────────────────────────────────────────────

def _load_history() -> list[list]:
    """Load evaluation history as rows for the Dataframe."""
    rows = _history_db.list_evaluations(limit=100)
    table = []
    for r in rows:
        import json
        agents = json.loads(r["per_agent_json"])
        agents_str = ", ".join(f"{k}: {v}" for k, v in agents.items())
        table.append([
            r["id"],
            r["timestamp"][:16].replace("T", " "),
            r["pdf_name"],
            r["eval_type"],
            r["score"],
            r["nivel_general"] or "-",
            agents_str or "-",
        ])
    return table


def _view_report(eval_id) -> str:
    """Read the HTML report file for a given evaluation ID."""
    if not eval_id:
        return "<p>Ingresa un ID de evaluacion.</p>"
    try:
        eval_id = int(eval_id)
    except (TypeError, ValueError):
        return "<p>ID invalido.</p>"
    path = _history_db.get_html_path(eval_id)
    if not path:
        return "<p>No se encontro reporte para ese ID.</p>"
    p = Path(path)
    if not p.exists():
        return f"<p>Archivo no encontrado: <code>{path}</code></p>"
    return p.read_text(encoding="utf-8")


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
            f"Evalua planeaciones didacticas con IA ({LLM_MODEL_DISPLAY}) "
            "o consulta los documentos curriculares."
        )

        # Rate limit bar
        usage_display = gr.HTML(value=_get_usage_display)

        with gr.Tab("Evaluar"):
            pdf_input = gr.File(
                label="Sube la planeacion en PDF",
                file_types=[".pdf"],
                type="filepath",
            )
            eval_mode = gr.Radio(
                choices=["3 Expertos (Rubrica)", "5 Expertos (Delphi)"],
                value="3 Expertos (Rubrica)",
                label="Modo de evaluacion",
            )
            gr.Markdown(
                "- **3 Expertos (Rubrica):** Pedagogo, Profesor y Tecnico evaluan con rubrica "
                "de criterios. Resultado: % de cumplimiento.\n"
                "- **5 Expertos (Delphi):** 5 expertos IA (Dr. Critico, Dra. Multiliteracidades, "
                "etc.) debaten desde marcos teoricos. Resultado: puntuacion 1-10 en 6 dimensiones."
            )
            eval_btn = gr.Button("Evaluar", variant="primary")
            eval_output = gr.Markdown(label="Resultado")
            report_file = gr.File(
                label="Reporte HTML descargable",
                interactive=False,
            )
            eval_html_display = gr.HTML(label="Reporte")

            eval_btn.click(
                fn=_run_unified_eval,
                inputs=[pdf_input, eval_mode],
                outputs=[eval_output, report_file, eval_html_display, usage_display],
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

        with gr.Tab("Como funciona"):
            with gr.Accordion("Flujo de evaluacion (Rubrica)", open=True):
                gr.HTML(_metodologia_html)
            with gr.Accordion("Panel Delphi (5 expertos) — Resumen", open=False):
                gr.HTML(_delphi_summary_html)
            with gr.Accordion("Panel Delphi — Detalle de la simulacion", open=False):
                gr.HTML(_delphi_detail_html)

        with gr.Tab("Historial"):
            gr.Markdown("### Historial de evaluaciones — registro publico")
            refresh_btn = gr.Button("Actualizar", variant="secondary")
            history_table = gr.Dataframe(
                headers=["ID", "Fecha", "Archivo", "Tipo", "Score", "Nivel", "Expertos"],
                datatype=["number", "str", "str", "str", "number", "str", "str"],
                value=_load_history,
                interactive=False,
            )
            with gr.Row():
                report_id_input = gr.Number(label="ID de evaluacion", precision=0)
                view_report_btn = gr.Button("Ver reporte", variant="primary")
            report_html_output = gr.HTML(label="Reporte")

            refresh_btn.click(fn=_load_history, outputs=[history_table])
            view_report_btn.click(
                fn=_view_report,
                inputs=[report_id_input],
                outputs=[report_html_output],
            )

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
