"""
MediBook LangChain pipeline orchestration.

Flow per message:
  1. Load session memory
  2. Classify intent
  3. Extract slots
  4. (Stage 4 will call appointment_service here)
"""

from langchain_pipeline.intent_chain import classify_intent
from langchain_pipeline.memory import get_history_text, save_turn
from langchain_pipeline.response_chain import generate_response
from langchain_pipeline.slot_extraction import extract_slots


def process_message(
    session_id: str,
    message: str,
    *,
    save_to_memory: bool = False,
    bot_response: str | None = None,
) -> dict:
    """
    Run intent classification + slot extraction for a patient message.

    Returns dict with intent, slots, and history used.
    If save_to_memory=True, also stores the turn (requires bot_response).
    """
    history = get_history_text(session_id)
    intent = classify_intent(message, history)
    slots = extract_slots(message, history, intent=intent)

    if save_to_memory and bot_response:
        save_turn(session_id, message, bot_response)

    return {
        "intent": intent,
        "slots": slots,
        "history": history,
    }


def process_message_with_response(
    session_id: str,
    message: str,
    structured_result: dict,
) -> dict:
    """
    Full pipeline helper for Stage 4: classify, extract, generate reply, save memory.
    """
    history = get_history_text(session_id)
    intent = classify_intent(message, history)
    slots = extract_slots(message, history, intent=intent)
    reply = generate_response(structured_result)
    save_turn(session_id, message, reply)

    return {
        "intent": intent,
        "slots": slots,
        "reply": reply,
        "structured_data": structured_result,
    }
