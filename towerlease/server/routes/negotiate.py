"""
Negotiation endpoint.

POST /api/negotiate -- kicks off the negotiation agent, generates a
structured brief, and returns it along with a session ID for follow-up.
"""
from fastapi import APIRouter

from towerlease.server.schemas import NegotiateRequest, NegotiateResponse
from towerlease.server import session_store

router = APIRouter()


@router.post("/api/negotiate", response_model=NegotiateResponse)
def negotiate(request: NegotiateRequest):
    """Return a pre-populated stub response without calling OpenAI."""
    session_id = session_store.create_session([
        {"role": "system", "content": "Stub session."},
    ])
    return NegotiateResponse(
        session_id=session_id,
        brief=(
            f"Tower {request.tower_id} is leased from {request.provider} in the {request.region} region. "
            f"The current monthly rate of ${request.current_monthly_rate}/mo is above the regional median. "
            "AT&T has strong leverage given multi-tenant occupancy and upcoming lease expiry. "
            "Recommend opening negotiations at a 15% reduction with a walk-away at 3% below current rate."
        ),
        recommended_opening_rate=int(request.current_monthly_rate * 0.85),
        walk_away_rate=int(request.current_monthly_rate * 0.97),
        key_leverage_points=[
            "Current rate is above regional median",
            "Lease expiring soon — urgency for both parties",
            "AT&T portfolio leverage with 2000+ national leases",
            "Multi-tenant occupancy reduces provider leverage",
        ],
        comparable_rates={
            "low": int(request.current_monthly_rate * 0.75),
            "median": int(request.current_monthly_rate * 0.95),
            "high": int(request.current_monthly_rate * 1.20),
        },
        provider_context=f"Stub: {request.provider} is a standard commercial tower provider.",
        region_context=f"Stub: {request.region} region rates are trending slightly down.",
        negotiation_history_summary="Stub: No historical lease data loaded (stub mode).",
        crm_intelligence="Stub: No CRM intelligence loaded (stub mode).",
    )
