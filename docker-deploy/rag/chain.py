"""Conversational RAG chain over curricular documents."""

from __future__ import annotations

from langchain_classic.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI

from config import LLM_MODEL, RAG_TEMPERATURE
from rag.retriever import get_retriever

SYSTEM_MESSAGE = (
    "Eres un asistente experto en el análisis curricular del bloque MT1001B. "
    "Responde en español usando los documentos proporcionados como contexto. "
    "Si la información no está en los documentos, indícalo claramente. "
    "Cita las fuentes cuando sea posible."
)


def build_rag_chain() -> ConversationalRetrievalChain:
    """Build a conversational RAG chain with history support."""
    llm = ChatOpenAI(
        model=LLM_MODEL,
        temperature=RAG_TEMPERATURE,
    )
    retriever = get_retriever()

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        verbose=False,
    )
    return chain
