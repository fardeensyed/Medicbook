"""Natural language response generation chain."""

import json
from typing import Any

from langchain_core.output_parsers import StrOutputParser

from langchain_pipeline.llm import get_llm
from langchain_pipeline.prompts import RESPONSE_GENERATION_PROMPT


def build_response_chain():
    """LangChain LCEL chain: prompt → Groq LLM → string parser."""
    llm = get_llm(temperature=0.3)
    return RESPONSE_GENERATION_PROMPT | llm | StrOutputParser()


def generate_response(structured_result: dict[str, Any]) -> str:
    """Turn a structured booking/slots/cancellation result into a natural language reply."""
    chain = build_response_chain()
    return chain.invoke(
        {"structured_result": json.dumps(structured_result, indent=2, default=str)}
    ).strip()
