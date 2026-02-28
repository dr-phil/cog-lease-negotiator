"""
Negotiation endpoint.

POST /api/negotiate -- kicks off the negotiation agent, generates a
structured brief, and returns it along with a session ID for follow-up.
"""
from fastapi import APIRouter

from towerlease.server.schemas import NegotiateRequest, NegotiateResponse
from towerlease.agents.negotiation_agent import run_negotiation_agent
from towerlease.agents.brief_generator import generate_brief
from towerlease.server import session_store

router = APIRouter()


@router.post("/api/negotiate", response_model=NegotiateResponse)
def negotiate(request: NegotiateRequest):
    """Generate a negotiation brief for a tower lease renewal.

    This endpoint:
    1. Runs the negotiation agent (multiple tool calls)
    2. Passes the raw output through the brief generator
    3. Stores the conversation in session state for follow-up
    4. Returns the structured brief
    """
    lease_data = {
        "tower_id": request.tower_id,
        "current_monthly_rate": request.current_monthly_rate,
        "lease_expiry": request.lease_expiry,
        "lease_years_remaining": request.lease_years_remaining,
    }

    # Step 1: Run the negotiation agent
    raw_analysis, messages = run_negotiation_agent(
        tower_id=request.tower_id,
        lease_data=lease_data,
        provider=request.provider,
        region=request.region,
    )

    # Step 2: Generate structured brief
    brief_data = generate_brief(raw_analysis, lease_data)

    # Step 3: Store session for follow-up
    session_id = session_store.create_session(messages)

    # Step 4: Build response
    return NegotiateResponse(
        session_id=session_id,
        brief=brief_data["brief"],
        recommended_opening_rate=brief_data["recommended_opening_rate"],
        walk_away_rate=brief_data["walk_away_rate"],
        key_leverage_points=brief_data["key_leverage_points"],
        comparable_rates=brief_data["comparable_rates"],
        provider_context=brief_data["provider_context"],
        region_context=brief_data["region_context"],
        negotiation_history_summary=brief_data["negotiation_history_summary"],
        crm_intelligence=brief_data["crm_intelligence"],
    )
