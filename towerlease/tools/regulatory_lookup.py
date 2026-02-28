"""
Regulatory lookup tool.

Returns mock state/local regulatory context for tower siting in a given
region. Includes relevant statutes, recent zoning decisions, and pending
legislation.

In production this queries the AT&T regulatory affairs database.
That system is maintained by the legal team and is... not great.
# TODO: ask regulatory affairs to add an API instead of scraping their
# SharePoint site. JIRA-1788
"""
import hashlib
import random


_STATE_STATUTES = {
    "northeast": [
        {"state": "NY", "statute": "NY Gen. City Law § 81-a", "summary": "Municipalities may regulate tower placement but cannot impose blanket prohibitions"},
        {"state": "CT", "statute": "CT Gen. Stat. § 16-50g", "summary": "Connecticut Siting Council has exclusive jurisdiction over cell tower approvals"},
        {"state": "NJ", "statute": "NJ Stat. § 40:55D-46.1", "summary": "Cell towers permitted in industrial zones by right; conditional use in commercial zones"},
        {"state": "MA", "statute": "MA Gen. Laws ch. 40A § 3", "summary": "Zoning cannot prohibit towers on state-owned land; local review for private sites"},
    ],
    "southeast": [
        {"state": "FL", "statute": "FL Stat. § 365.172", "summary": "Florida has streamlined tower permitting under the Advanced Wireless Infrastructure Act"},
        {"state": "GA", "statute": "GA Code § 36-66B-1", "summary": "Georgia Broadband Services Act limits local review timelines to 90 days"},
        {"state": "NC", "statute": "NC Gen. Stat. § 160D-935", "summary": "North Carolina limits tower setback requirements to tower height + 10 feet"},
        {"state": "VA", "statute": "VA Code § 15.2-2316.3", "summary": "Virginia requires localities to approve co-locations within 60 days"},
    ],
    "midwest": [
        {"state": "OH", "statute": "OH Rev. Code § 4939.031", "summary": "Ohio Power Siting Board has jurisdiction for towers over 50 feet"},
        {"state": "IL", "statute": "220 ILCS 5/5-102", "summary": "Illinois Commerce Commission oversees tower siting; no separate local approval needed"},
        {"state": "IN", "statute": "IC 8-1-32.3-19", "summary": "Indiana limits local tower review to 90 days; deemed approved if no action"},
        {"state": "MN", "statute": "MN Stat. § 237.163", "summary": "Minnesota requires colocation accommodation on existing structures before new builds"},
    ],
    "west": [
        {"state": "CA", "statute": "CA Gov. Code § 65850.6", "summary": "CEQA environmental review required for new tower sites; streamlined for co-locations"},
        {"state": "WA", "statute": "RCW 35.99.030", "summary": "Washington SEPA review required; 150-day shot clock for local decisions"},
        {"state": "CO", "statute": "CRS § 29-27-402", "summary": "Colorado limits local aesthetic requirements for small cells on existing structures"},
        {"state": "AZ", "statute": "ARS § 9-591", "summary": "Arizona prohibits local moratoria on wireless facility permits"},
    ],
}

_RECENT_DECISIONS = [
    "Zoning board approved 120-ft monopole after AT&T demonstrated coverage gap via propagation study",
    "County denied tower application citing insufficient setback; AT&T appealed under TCA Section 332(c)(7)",
    "Municipality approved co-location modification within 45-day shot clock",
    "Planning commission required additional environmental review for ground mount near wetlands",
    "City council approved water tower antenna installation with aesthetic conditions",
    "Variance granted for rooftop installation exceeding height limit by 15 feet",
]

_PENDING_LEGISLATION = [
    "State bill to reduce tower permit review timeline from 150 to 90 days -- committee vote pending",
    "Proposed legislation to exempt 5G small cells from local zoning review entirely",
    "County considering moratorium on new tower construction pending updated comprehensive plan",
    "State wireless infrastructure modernization act -- would streamline permitting statewide",
    None,  # sometimes there's nothing pending
    None,
]


def lookup(region, tower_type):
    """Look up regulatory context for tower siting.

    Args:
        region: one of northeast, southeast, midwest, west
        tower_type: one of rooftop, ground_mount, water_tower, monopole

    Returns:
        dict with regulatory context
    """
    seed_str = "{}-{}".format(region, tower_type)
    seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    statutes = _STATE_STATUTES.get(region, _STATE_STATUTES["southeast"])
    relevant_statutes = rng.sample(statutes, min(2, len(statutes)))

    recent = rng.sample(_RECENT_DECISIONS, 2)
    pending = rng.choice(_PENDING_LEGISLATION)

    result = {
        "region": region,
        "tower_type": tower_type,
        "relevant_statutes": relevant_statutes,
        "recent_zoning_decisions": recent,
        "pending_legislation": pending,
        "regulatory_risk_level": rng.choice(["low", "moderate", "elevated"]),
        "estimated_new_site_timeline_months": rng.randint(4, 18),
        "negotiation_impact": (
            "Longer new-site timelines in this region increase the value of "
            "existing lease renewals. Estimated %d months for a new %s site "
            "through the full permitting process."
            % (rng.randint(6, 18), tower_type.replace("_", " "))
        ),
    }
    return result


TOOL_DEFINITION = {
    "name": "regulatory_lookup",
    "description": (
        "Look up state and local regulatory context for tower siting in a "
        "given region. Returns relevant statutes, recent zoning decisions, "
        "and pending legislation that may affect negotiations. Use this to "
        "understand the regulatory environment and permitting timelines."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "region": {
                "type": "string",
                "description": "Region identifier: northeast, southeast, midwest, or west",
            },
            "tower_type": {
                "type": "string",
                "description": "Type of tower: rooftop, ground_mount, water_tower, or monopole",
            },
        },
        "required": ["region", "tower_type"],
    },
}
