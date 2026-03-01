# Wraps the internal LeaseTrack API -- see confluence: infra/leasetrack-api-docs
# Rate limited to 10 req/min in prod, use tower_id batching where possible
# Auth handled via internal mTLS cert, mocked here for local dev
"""
Lease history service.

Simulates AT&T's internal LeaseTrack API. Given a tower_id, returns
historical lease data including past rates, negotiators, outcome notes,
and special clauses.

Uses hashlib for deterministic-but-varied results per tower.
"""
import hashlib
import random


_NEGOTIATOR_NAMES = [
    "J. Martinez",
    "R. Thompson",
    "S. Chen",
    "M. Williams",
    "K. Patel",
    "D. Kim",
    "A. Johnson",
    "T. Nguyen",
    "L. Garcia",
    "B. Anderson",
]

_OUTCOME_NOTES_TEMPLATES = [
    "Landlord requested {pct_ask}% increase, settled at {pct_settled}%. Escalation clause changed from flat 3% to CPI+1%.",
    "Landlord initially firm on {pct_ask}% increase. After presenting comparable data, agreed to {pct_settled}%. Added right of first refusal.",
    "Smooth renewal. Landlord accepted {pct_settled}% increase without pushback. No clause changes.",
    "Contentious negotiation -- landlord threatened non-renewal. Settled at {pct_settled}% with extended 10yr term.",
    "Landlord represented by outside counsel. Pushed for {pct_ask}% increase, settled at {pct_settled}% after 3 rounds.",
    "Landlord amenable to rate reduction of {pct_settled}% in exchange for 15yr term commitment and co-location consent waiver.",
    "Renewal included equipment upgrade provisions. Rate increased {pct_settled}% but AT&T gained rooftop expansion rights.",
    "Landlord requested {pct_ask}% increase citing nearby commercial development. Settled at {pct_settled}% after market comp review.",
    "Quick negotiation -- landlord prioritized lease certainty over rate maximization. Flat {pct_settled}% increase accepted.",
    "Multi-round negotiation spanning 4 months. Landlord initially demanded {pct_ask}% increase. Final agreement at {pct_settled}% with CPI cap at 3%.",
]

_SPECIAL_CLAUSES = [
    "right_of_first_refusal",
    "co-location_consent_required",
    "equipment_upgrade_rights",
    "early_termination_penalty_waiver",
    "structural_modification_rights",
    "sublease_rights",
    "cpi_cap_3pct",
    "cpi_cap_4pct",
    "ground_lease_extension_option",
    "height_expansion_rights",
    "fiber_backhaul_easement",
    "generator_installation_rights",
]


def get_lease_history(tower_id):
    """Retrieve historical lease data for a given tower.

    Args:
        tower_id: AT&T tower identifier (e.g. ATT-TX-4821)

    Returns:
        dict with lease_history list, rate_trend, average_annual_escalation,
        last_negotiated date, and data_quality indicator
    """
    seed = int(hashlib.md5(tower_id.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    # Determine number of history entries based on hash
    # Some towers have rich history (6-8 entries, high quality)
    # Others have sparse history (2 entries, low quality)
    hash_val = int(hashlib.sha256(tower_id.encode()).hexdigest()[:4], 16)
    if hash_val % 5 == 0:
        num_entries = 2
        data_quality = "low"
    elif hash_val % 5 <= 2:
        num_entries = rng.randint(3, 4)
        data_quality = "medium"
    else:
        num_entries = rng.randint(5, 8)
        data_quality = "high"

    # Generate history entries going back from recent to oldest
    current_year = 2024
    base_rate = rng.randint(1200, 5000)
    history = []
    rate_values = []

    for i in range(num_entries):
        year = current_year - (i * rng.randint(1, 3))
        if year < 2010:
            year = 2010 + i

        # Rate generally increases over time (going backward means earlier = lower)
        escalation_factor = 1.0 + (i * rng.uniform(0.02, 0.06))
        monthly_rate = int(base_rate / escalation_factor)
        rate_values.append(monthly_rate)

        negotiator = rng.choice(_NEGOTIATOR_NAMES)

        pct_ask = rng.randint(8, 20)
        pct_settled = rng.randint(2, pct_ask - 1) if pct_ask > 3 else pct_ask
        template = rng.choice(_OUTCOME_NOTES_TEMPLATES)
        outcome_notes = template.format(pct_ask=pct_ask, pct_settled=pct_settled)

        num_clauses = rng.randint(0, 3)
        special_clauses = rng.sample(_SPECIAL_CLAUSES, num_clauses)

        history.append({
            "year": year,
            "monthly_rate": monthly_rate,
            "negotiator": negotiator,
            "outcome_notes": outcome_notes,
            "special_clauses": special_clauses,
        })

    # Sort by year ascending
    history.sort(key=lambda h: h["year"])

    # Determine rate trend
    if len(rate_values) >= 2:
        if rate_values[0] > rate_values[-1]:
            rate_trend = "increasing"
        elif rate_values[0] < rate_values[-1]:
            rate_trend = "decreasing"
        else:
            rate_trend = "stable"
    else:
        rate_trend = "insufficient_data"

    # Calculate average annual escalation
    if len(rate_values) >= 2 and rate_values[-1] > 0:
        years_span = max(num_entries, 1)
        total_change = (rate_values[0] - rate_values[-1]) / rate_values[-1]
        avg_escalation = round(total_change / years_span, 3)
    else:
        avg_escalation = 0.0

    # Last negotiated date
    last_year = max(h["year"] for h in history)
    last_month = rng.randint(1, 12)
    last_day = rng.randint(1, 28)
    last_negotiated = "%04d-%02d-%02d" % (last_year, last_month, last_day)

    return {
        "tower_id": tower_id,
        "lease_history": history,
        "rate_trend": rate_trend,
        "average_annual_escalation": avg_escalation,
        "last_negotiated": last_negotiated,
        "data_quality": data_quality,
    }


TOOL_DEFINITION = {
    "type": "function",
    "name": "get_lease_history",
    "description": (
        "Retrieve historical lease negotiation data for a tower from the "
        "internal LeaseTrack API. Returns past lease rates, negotiator names, "
        "outcome notes, special clauses, rate trends, and data quality indicators. "
        "Use this early in the analysis to understand AT&T's negotiation history "
        "with this specific site before pulling external market data."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "tower_id": {
                "type": "string",
                "description": "The AT&T tower identifier (e.g. ATT-TX-4821)",
            }
        },
        "required": ["tower_id"],
    },
}
