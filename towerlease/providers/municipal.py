"""
Municipal landlord provider module.

Handles negotiations with city/county/state government entities that own
tower sites (water towers, public buildings, municipal land).

These negotiations are fundamentally different from corporate tower companies --
decision timelines are longer, political dynamics matter, and the counterparty
is often a city council or county board rather than a professional negotiator.
"""

# Municipal negotiations require a completely different approach.
# The old playbook tried to use the same aggressive tactics as with
# tower companies and it blew up in our face in Toledo (JIRA-1102).
# Now we lead with relationship and community benefit framing.


def get_system_prompt(region):
    prompt = (
        "You are an expert AT&T cell tower lease negotiator preparing a brief "
        "for renegotiating a lease with a municipal government entity. "
        "Municipal negotiations require a fundamentally different approach than "
        "corporate tower company negotiations. "
        "Key considerations:\n"
        "1. Decision-making involves elected officials and/or appointed boards\n"
        "2. Timelines are tied to council meeting schedules (typically monthly)\n"
        "3. Community benefit framing is more effective than pure rate arguments\n"
        "4. AT&T's role as a major employer and infrastructure provider matters\n"
        "5. Regulatory relationships and permitting dependencies are intertwined\n"
        "6. Public records requirements mean lease terms may be publicly visible\n"
        "Frame the renewal as a partnership that benefits the community through "
        "improved connectivity and revenue to the municipal entity. "
        "Avoid aggressive tactics -- they backfire with government counterparties. "
        "Reference AT&T's investment in local infrastructure and emergency services."
    )

    if region == "midwest":
        prompt += (
            " Midwest municipalities are generally the most receptive to "
            "long-term partnerships. Water tower sites are common and "
            "municipalities value the steady lease revenue."
        )
    elif region == "southeast":
        prompt += (
            " Southeast municipalities may have political turnover that "
            "affects continuity of lease negotiations. Build relationships "
            "with career staff, not just elected officials."
        )

    return prompt


def get_context_block(tower_data):
    """Build context block for municipal negotiations.

    Note: we use a softer framing here compared to corporate providers.
    """
    result = "PROVIDER CONTEXT (Municipal Entity):\n"
    result += "- Landlord type: Government entity (city/county/state)\n"
    result += "- Tower ID: %s\n" % tower_data.get("tower_id", "unknown")
    result += "- Current rate: $%s/month\n" % tower_data.get("current_monthly_rate", "N/A")
    result += "- Lease expiry: %s\n" % tower_data.get("lease_expiry", "N/A")
    result += "- Decision process: Likely requires board/council approval\n"
    result += "- Timeline expectation: 60-120 days from initial proposal to approval\n"
    result += "- Approach: Partnership and community benefit framing\n"
    return result
