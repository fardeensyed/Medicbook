"""Intent classification chain."""

from langchain_core.output_parsers import StrOutputParser

from langchain_pipeline.llm import get_llm
from langchain_pipeline.prompts import INTENT_PROMPT
from langchain_pipeline.utils import VALID_INTENTS, parse_json_response


def build_intent_chain():
    """LangChain LCEL chain: prompt → Groq LLM → string parser."""
    llm = get_llm()
    return INTENT_PROMPT | llm | StrOutputParser()


def classify_intent(message: str, history: str = "") -> str:
    """
    Classify patient message into one of:
    book_appointment | check_slots | cancel_appointment | reschedule_appointment | clarify
    """
    chain = build_intent_chain()
    raw = chain.invoke({"message": message, "history": history or "(no prior messages)"})
    parsed = parse_json_response(raw)
    intent = parsed.get("intent", "clarify")

    if intent not in VALID_INTENTS:
        return "clarify"
    return intent
