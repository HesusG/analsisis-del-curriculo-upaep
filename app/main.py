"""Chainlit entry point — Evaluador Curricular + RAG Chatbot."""

from __future__ import annotations

import tempfile
from pathlib import Path

import chainlit as cl

from config import CHROMA_DIR
from evaluation.pipeline import run_evaluation
from rag.chain import build_rag_chain
from rag.ingest import ingest_sources


@cl.on_chat_start
async def on_chat_start():
    """Initialize RAG chain and welcome the user."""
    # Ingest sources if ChromaDB doesn't exist yet
    if not CHROMA_DIR.exists() or not any(CHROMA_DIR.iterdir()):
        await cl.Message(content="Indexando documentos curriculares por primera vez...").send()
        ingest_sources()

    # Build RAG chain and store in session
    chain = build_rag_chain()
    cl.user_session.set("rag_chain", chain)
    cl.user_session.set("chat_history", [])


@cl.on_message
async def on_message(message: cl.Message):
    """Route: PDF upload → evaluation pipeline; text → RAG chat."""
    # Check for PDF attachments
    pdf_files = [
        f for f in (message.elements or [])
        if f.mime and f.mime == "application/pdf"
    ]

    if pdf_files:
        await handle_evaluation(pdf_files[0])
    else:
        await handle_chat(message.content)


async def handle_evaluation(pdf_element: cl.Element):
    """Run 3-expert evaluation on uploaded PDF and return report."""
    msg = cl.Message(content="Evaluando con 3 expertos en paralelo...")
    await msg.send()

    # Save uploaded file to temp location
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(Path(pdf_element.path).read_bytes())
        tmp_path = tmp.name

    try:
        synthesis, html_path = await run_evaluation(tmp_path)

        # Build summary message
        summary_lines = [
            f"## Evaluación completada",
            f"",
            f"**Cumplimiento promedio:** {synthesis.average_compliance:.1f}%",
            f"**Nivel:** {synthesis.nivel_general.value}",
            f"",
            f"### Por experto:",
        ]
        for key, ev in synthesis.per_agent.items():
            summary_lines.append(
                f"- **{ev.metadata.evaluador}**: {ev.resumen_ejecutivo.porcentaje_cumplimiento:.1f}%"
            )

        summary_lines.extend([
            f"",
            f"### Fortalezas:",
        ])
        for s in synthesis.strengths[:5]:
            summary_lines.append(f"- {s}")

        summary_lines.extend([
            f"",
            f"### Areas criticas:",
        ])
        for a in synthesis.critical_areas[:5]:
            summary_lines.append(f"- {a}")

        summary_lines.append(f"\nDescarga el reporte completo abajo.")

        # Send summary + downloadable HTML
        elements = [
            cl.File(
                name=Path(html_path).name,
                path=html_path,
                display="inline",
            )
        ]
        await cl.Message(
            content="\n".join(summary_lines),
            elements=elements,
        ).send()

    except Exception as e:
        await cl.Message(content=f"Error durante la evaluación: {e}").send()
    finally:
        Path(tmp_path).unlink(missing_ok=True)


async def handle_chat(user_message: str):
    """RAG chat with conversational history."""
    chain = cl.user_session.get("rag_chain")
    chat_history = cl.user_session.get("chat_history") or []

    msg = cl.Message(content="")
    await msg.send()

    result = await cl.make_async(chain.invoke)(
        {"question": user_message, "chat_history": chat_history}
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

    # Update history
    chat_history.append((user_message, answer))
    cl.user_session.set("chat_history", chat_history)

    msg.content = answer
    await msg.update()
