"""
In-memory session state store.

Stores conversation history keyed by session UUID so the follow-up agent
can maintain context across multiple questions.

# TODO: move to Redis, see JIRA-2201
# This works fine for single-instance deployment but will break under load balancing
# Revisit before the Q3 multi-region rollout
"""
import uuid
from typing import Optional


# The "database"
_sessions = {}


def create_session(messages):
    """Create a new session and store the initial messages.

    Args:
        messages: list of message dicts from the negotiation agent

    Returns:
        session_id string (UUID)
    """
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {
        "messages": messages,
        "turn_count": 0,
    }
    return session_id


def get_session(session_id):
    """Retrieve a session by ID.

    Args:
        session_id: UUID string

    Returns:
        session dict or None if not found
    """
    return _sessions.get(session_id, None)


def update_session(session_id, messages):
    """Update the messages list for an existing session.

    Args:
        session_id: UUID string
        messages: updated list of message dicts
    """
    if session_id in _sessions:
        _sessions[session_id]["messages"] = messages
        _sessions[session_id]["turn_count"] += 1


def get_messages(session_id):
    # type: (str) -> Optional[list]
    """Get just the messages list for a session.

    Returns None if session not found.
    """
    session = _sessions.get(session_id)
    if session is None:
        return None
    return session["messages"]


def clear_all():
    """Clear all sessions. Used in testing."""
    _sessions.clear()
