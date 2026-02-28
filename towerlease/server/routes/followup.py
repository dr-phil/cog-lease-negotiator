"""
Follow-up Q&A endpoint.

POST /api/followup -- accepts a session ID and question, returns an answer
using the existing conversation context.
"""
from fastapi import APIRouter, HTTPException

from towerlease.server.schemas import FollowupRequest, FollowupResponse
from towerlease.agents.followup_agent import handle_followup
from towerlease.server import session_store

router = APIRouter()


@router.post("/api/followup", response_model=FollowupResponse)
def followup(request: FollowupRequest):
    """Handle a follow-up question about a previously generated brief.

    Retrieves the conversation history from session store, passes it
    to the follow-up agent with the new question, and stores the
    updated conversation back.
    """
    messages = session_store.get_messages(request.session_id)

    if messages is None:
        raise HTTPException(
            status_code=404,
            detail="Session expired or not found — please generate a new brief.",
        )

    answer, updated_messages = handle_followup(messages, request.question)

    # Store the updated conversation back
    session_store.update_session(request.session_id, updated_messages)

    return FollowupResponse(
        answer=answer,
        session_id=request.session_id,
    )
