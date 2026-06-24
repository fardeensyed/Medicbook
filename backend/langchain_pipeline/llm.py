"""Groq LLM client via langchain-groq."""

import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
FALLBACK_MODEL = "mixtral-8x7b-32768"


def get_llm(model: str | None = None, temperature: float = 0.1) -> ChatGroq:
    """Return a configured Groq chat model. Reads GROQ_API_KEY from .env."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. Copy backend/.env.example to backend/.env "
            "and add your Groq API key."
        )

    return ChatGroq(
        model=model or DEFAULT_MODEL,
        temperature=temperature,
        groq_api_key=api_key,
    )
