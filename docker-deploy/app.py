"""Gradio entry point — Evaluador Curricular + RAG Chatbot."""

from __future__ import annotations

import os
from pathlib import Path

import gradio as gr

from evaluation.pipeline import run_evaluation

# ── Lazy RAG chain (only built on first use) ──────────────────────────
_rag_chain = None
_APP_PASSWORD = os.getenv("APP_PASSWORD", "UPAEP2026")


def _get_rag_chain():
    global _rag_chain
    if _rag_chain is None:
        from rag.chain import build_rag_chain
        _rag_chain = build_rag_chain()
    return _rag_chain


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
        progress(0.2, desc="Evaluando con 3 expertos en paralelo...")
        synthesis, html_path = await run_evaluation(pdf_filepath)

        progress(0.9, desc="Generando reporte...")

        # Build summary
        lines = [
            "## Evaluacion completada",
            "",
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

        lines.extend(["", "### Fortalezas:"])
        for s in synthesis.strengths[:5]:
            lines.append(f"- {s}")

        lines.extend(["", "### Areas criticas:"])
        for a in synthesis.critical_areas[:5]:
            lines.append(f"- {a}")

        progress(1.0, desc="Listo.")
        return "\n".join(lines), html_path

    except Exception as e:
        return f"Error durante la evaluacion: {e}", None


# ── Tab 2: RAG Chat ───────────────────────────────────────────────────

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
            "Evalua planeaciones didacticas con 3 expertos IA "
            "o consulta los documentos curriculares."
        )

        with gr.Tab("Evaluar Planeacion"):
            gr.Markdown("*Solo se aceptan archivos PDF por el momento.*")
            pdf_input = gr.File(
                label="Sube la planeacion en PDF",
                file_types=[".pdf"],
                type="filepath",
            )
            eval_btn = gr.Button("Evaluar con 3 expertos", variant="primary")
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
    demo.launch(server_name="0.0.0.0", server_port=7860, ssr_mode=False)
