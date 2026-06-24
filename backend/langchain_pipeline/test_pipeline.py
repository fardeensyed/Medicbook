"""
Standalone test script for the LangChain + Groq pipeline (Stage 3).

Run from the backend directory:
    python -m langchain_pipeline.test_pipeline

Requires GROQ_API_KEY in backend/.env
"""

import uuid

from langchain_pipeline.intent_chain import classify_intent
from langchain_pipeline.llm import get_llm
from langchain_pipeline.memory import clear_memory, get_history_text, save_turn
from langchain_pipeline.response_chain import generate_response
from langchain_pipeline.slot_extraction import extract_slots

SAMPLE_UTTERANCES = [
    "I want to see a cardiologist this Friday afternoon",
    "Cancel my appointment",
    "Do you have anything with Dr. Sharma tomorrow morning?",
    "Hi, I need help booking a visit",
    "Can I move my dermatology appointment to next Monday at 2pm?",
]


def print_result(label: str, message: str, history: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"Utterance: {message}")
    print("-" * 60)

    intent = classify_intent(message, history)
    slots = extract_slots(message, history, intent=intent)

    print(f"Intent:  {intent}")
    print(f"Slots:   {slots}")

    # Demo response generation for a mock structured result
    mock_result = {
        "type": "clarification" if intent == "clarify" else intent,
        "intent": intent,
        "extracted_slots": slots,
        "needs_clarification": [k for k, v in slots.items() if v is None],
    }
    reply = generate_response(mock_result)
    print(f"Reply:   {reply}")


def main():
    try:
        get_llm()
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return

    session_id = f"test-{uuid.uuid4().hex[:8]}"
    clear_memory(session_id)

    print("MediBook LangChain Pipeline — Stage 3 Test")
    print(f"Session: {session_id}")

    history = get_history_text(session_id)

    for i, utterance in enumerate(SAMPLE_UTTERANCES, start=1):
        print_result(f"Sample {i}", utterance, history)
        # Simulate memory update for multi-turn context in later samples
        if i == 1:
            save_turn(
                session_id,
                utterance,
                "I can help you book with Cardiology. Which day works best for you?",
            )
            history = get_history_text(session_id)

    print(f"\n{'=' * 60}")
    print("Stage 3 pipeline test complete.")


if __name__ == "__main__":
    main()
