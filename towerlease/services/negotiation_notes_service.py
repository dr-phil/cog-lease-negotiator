# Pulls from NegotiatorCRM -- the internal Salesforce org
# Notes are free-text, quality varies significantly by region
# Some negotiators use it religiously, others barely at all -- handle sparse data gracefully
"""
Negotiation notes service.

Simulates AT&T's internal NegotiatorCRM (Salesforce org). Given a provider
and optional landlord_id, returns relationship intelligence including
negotiation notes, known sticking points, and committed positions.

Providers with sparse CRM data return sparse_data_warning: true.
"""


_PROVIDER_DATA = {
    "crown_castle": {
        "provider": "crown_castle",
        "relationship_tier": "strategic",
        "at_relationship_manager": "Sarah Chen, Tower Leasing Director",
        "known_sticking_points": [
            "Crown Castle consistently pushes back on CPI caps",
            "Escalation clause language is non-negotiable per their 2023 policy update",
            "CC legal team requires 90-day advance notice for any lease modification",
        ],
        "negotiation_notes": [
            {
                "date": "2023-11-02",
                "author": "R. Thompson",
                "note": "CC regional director indicated flexibility on term length in exchange for rate concessions. Worth exploring 10yr vs 5yr tradeoff.",
            },
            {
                "date": "2023-08-15",
                "author": "S. Chen",
                "note": "CC pushing standardized lease templates across portfolio. Less room for custom clause negotiation but faster turnaround.",
            },
            {
                "date": "2023-03-22",
                "author": "K. Patel",
                "note": "CC open to co-location consent streamlining if AT&T commits to 3+ year equipment upgrade schedule.",
            },
        ],
        "committed_positions": [
            "AT&T committed in 2022 master agreement to not pursue co-location disputes on CC towers through 2025",
            "CC committed to 60-day lease amendment turnaround for AT&T portfolio towers",
        ],
        "crm_data_quality": "high",
        "sparse_data_warning": False,
    },
    "american_tower": {
        "provider": "american_tower",
        "relationship_tier": "strategic",
        "at_relationship_manager": "Michael Torres, Senior Lease Manager",
        "known_sticking_points": [
            "American Tower has strict internal rate floors -- rarely negotiates below market median",
            "ATC requires environmental compliance documentation for any structural modifications",
            "ATC legal insists on arbitration clauses in all new agreements",
        ],
        "negotiation_notes": [
            {
                "date": "2024-01-10",
                "author": "M. Williams",
                "note": "ATC willing to discuss portfolio-level rate adjustments if AT&T consolidates renewals. Bundle 5+ towers for better leverage.",
            },
            {
                "date": "2023-09-05",
                "author": "D. Kim",
                "note": "ATC regional VP mentioned Q4 budget pressure -- may be more flexible on rates for early renewals before fiscal year end.",
            },
        ],
        "committed_positions": [
            "AT&T committed to equipment standardization on ATC towers per 2023 framework agreement",
            "ATC committed to waiving early termination fees for towers in AT&T FirstNet buildout areas",
        ],
        "crm_data_quality": "high",
        "sparse_data_warning": False,
    },
    "sba_communications": {
        "provider": "sba_communications",
        "relationship_tier": "preferred",
        "at_relationship_manager": "Jennifer Park, Regional Lease Coordinator",
        "known_sticking_points": [
            "SBA has been aggressive on escalation clauses since 2022 -- pushing CPI+2% minimum",
            "SBA requires AT&T to absorb structural analysis costs for equipment upgrades",
        ],
        "negotiation_notes": [
            {
                "date": "2023-12-18",
                "author": "A. Johnson",
                "note": "SBA account team restructured in Q4 2023. New regional director more data-driven -- come prepared with market comps.",
            },
            {
                "date": "2023-06-30",
                "author": "T. Nguyen",
                "note": "SBA responsive to long-term commitment. Offered 4% rate reduction for 15yr term on last negotiation.",
            },
        ],
        "committed_positions": [
            "SBA committed to priority processing for AT&T FirstNet co-locations through 2026",
        ],
        "crm_data_quality": "medium",
        "sparse_data_warning": False,
    },
    "municipal": {
        "provider": "municipal",
        "relationship_tier": "transactional",
        "at_relationship_manager": "Unassigned -- handled by regional team",
        "known_sticking_points": [
            "Municipal negotiations subject to public meeting schedules and council approval",
        ],
        "negotiation_notes": [],
        "committed_positions": [],
        "crm_data_quality": "low",
        "sparse_data_warning": True,
    },
    "rural_individual": {
        "provider": "rural_individual",
        "relationship_tier": "transactional",
        "at_relationship_manager": "Unassigned -- handled by regional team",
        "known_sticking_points": [
            "Individual landlords vary widely in sophistication and expectations",
        ],
        "negotiation_notes": [],
        "committed_positions": [],
        "crm_data_quality": "low",
        "sparse_data_warning": True,
    },
}

# Fallback for unknown providers
_DEFAULT_SPARSE = {
    "relationship_tier": "unknown",
    "at_relationship_manager": "Unassigned",
    "known_sticking_points": [],
    "negotiation_notes": [],
    "committed_positions": [],
    "crm_data_quality": "low",
    "sparse_data_warning": True,
}


def get_negotiation_notes(provider, landlord_id=None):
    """Retrieve negotiation intelligence for a provider.

    Args:
        provider: provider identifier (e.g. crown_castle, american_tower)
        landlord_id: optional landlord identifier for more specific lookup

    Returns:
        dict with relationship tier, negotiation notes, sticking points,
        committed positions, and data quality indicators
    """
    data = _PROVIDER_DATA.get(provider)

    if data is None:
        result = dict(_DEFAULT_SPARSE)
        result["provider"] = provider
        return result

    # Return a copy so callers can't mutate the source data
    result = {
        "provider": data["provider"],
        "relationship_tier": data["relationship_tier"],
        "at_relationship_manager": data["at_relationship_manager"],
        "known_sticking_points": list(data["known_sticking_points"]),
        "negotiation_notes": list(data["negotiation_notes"]),
        "committed_positions": list(data["committed_positions"]),
        "crm_data_quality": data["crm_data_quality"],
        "sparse_data_warning": data["sparse_data_warning"],
    }

    # If landlord_id is provided, append a note about it
    if landlord_id:
        result["landlord_id"] = landlord_id
        result["landlord_note"] = (
            "Landlord-specific lookup for %s -- no additional records found in CRM."
            % landlord_id
        )

    return result


TOOL_DEFINITION = {
    "type": "function",
    "name": "get_negotiation_notes",
    "description": (
        "Retrieve negotiation intelligence from the internal NegotiatorCRM "
        "(Salesforce org) for a given tower provider. Returns relationship tier, "
        "known sticking points, historical negotiation notes, and committed "
        "positions. Use this early in analysis to understand the relationship "
        "context before pulling external market data."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "provider": {
                "type": "string",
                "description": "Provider identifier: crown_castle, american_tower, sba_communications, municipal, or rural_individual",
            },
            "landlord_id": {
                "type": "string",
                "description": "Optional landlord identifier for landlord-specific notes",
            },
        },
        "required": ["provider"],
    },
}
