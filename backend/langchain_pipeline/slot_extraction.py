"""Slot extraction chain."""

from langchain_core.output_parsers import StrOutputParser

from langchain_pipeline.llm import get_llm
from langchain_pipeline.prompts import SLOT_EXTRACTION_PROMPT
from langchain_pipeline.utils import normalize_slots, parse_json_response


def build_slot_extraction_chain():
    """LangChain LCEL chain: prompt → Groq LLM → string parser."""
    llm = get_llm()
    return SLOT_EXTRACTION_PROMPT | llm | StrOutputParser()


def extract_slots(message: str, history: str = "", intent: str = "book_appointment") -> dict[str, str | None]:
    """
    Extract department, doctor_name, preferred_date, preferred_time
    from the message and conversation history.
    """
    chain = build_slot_extraction_chain()
    raw = chain.invoke(
        {
            "message": message,
            "history": history or "(no prior messages)",
            "intent": intent,
        }
    )
    parsed = parse_json_response(raw)
    return normalize_slots(parsed)
