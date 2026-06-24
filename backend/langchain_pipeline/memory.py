"""Session-scoped ConversationBufferMemory for multi-turn chat."""

from langchain_classic.memory import ConversationBufferMemory

# In-memory store keyed by session_id.
# NOTE: For production, replace this dict with Redis or another shared store
# so memory survives restarts and works across multiple server workers.
_session_memories: dict[str, ConversationBufferMemory] = {}


def get_memory(session_id: str) -> ConversationBufferMemory:
    """Return (or create) a ConversationBufferMemory for the given session."""
    if session_id not in _session_memories:
        _session_memories[session_id] = ConversationBufferMemory(
            memory_key="history",
            return_messages=False,
        )
    return _session_memories[session_id]


def get_history_text(session_id: str) -> str:
    """Load conversation history as a plain-text string for prompt injection."""
    memory = get_memory(session_id)
    variables = memory.load_memory_variables({})
    history = variables.get("history", "")
    return history if history else "(no prior messages)"


def save_turn(session_id: str, user_message: str, bot_response: str) -> None:
    """Persist one user/assistant exchange into session memory."""
    memory = get_memory(session_id)
    memory.save_context({"input": user_message}, {"output": bot_response})


def clear_memory(session_id: str) -> None:
    """Remove memory for a session (useful for testing)."""
    _session_memories.pop(session_id, None)
