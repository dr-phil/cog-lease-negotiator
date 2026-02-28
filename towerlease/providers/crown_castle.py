"""
Crown Castle provider module.

Crown Castle International (CCI) is the largest US tower company by site count.
AT&T has ~2,400 active leases with Crown Castle nationally.
"""

# Crown Castle renegotiated master terms with AT&T in 2021 -- new standard
# escalation is CPI+1% vs the old flat 3%. Make sure comparables reflect post-2021 leases.
# See confluence: tower-leasing/crown-castle-master-agreement-2021

# NOTE: Crown Castle acquired Lightower in 2017 and some of those legacy sites
# still show up under the old Lightower entity in property records. The
# property_lookup tool should handle this but double-check if you see mismatches.


def get_system_prompt(region):
    """Build system prompt for Crown Castle negotiations.

    Args:
        region: one of northeast, southeast, midwest, west
    """
    base = (
        "You are an expert AT&T cell tower lease negotiator preparing a brief "
        "for renegotiating a lease with Crown Castle International. "
        "AT&T maintains over 2,400 active tower leases with Crown Castle nationally, "
        "making AT&T one of their largest tenants. This portfolio leverage is your "
        "primary negotiating asset. "
        "Crown Castle's standard post-2021 escalation clause is CPI+1%% annually. "
        "Any lease still on the old flat 3%% escalation should be flagged as an "
        "opportunity to negotiate down to CPI+1%% or better. "
        "Focus on market rate benchmarking -- Crown Castle responds to data-driven "
        "arguments backed by comparable lease rates in the same market. "
        "Reference AT&T's willingness to consolidate tower providers in the region "
        "as additional leverage."
    )

    if region == "northeast":
        base += (
            " In the Northeast, Crown Castle has significant rooftop inventory "
            "in urban markets. Their urban sites tend to be priced at a premium "
            "but there is room to negotiate given AT&T's volume commitment."
        )
    elif region == "southeast":
        base += (
            " In the Southeast, Crown Castle is actively competing with SBA "
            "and American Tower for new builds. Use the competitive landscape "
            "to argue for rate reductions on existing sites."
        )
    elif region == "midwest":
        base += (
            " In the Midwest, Crown Castle has a thinner portfolio outside "
            "Chicago metro. AT&T has more alternative site options here, "
            "which strengthens the negotiating position."
        )
    elif region == "west":
        base += (
            " In the West, Crown Castle's permitting relationships in California "
            "are valuable but AT&T should not overpay for permitting convenience. "
            "Reference ground mount alternatives where available."
        )

    return base


def get_context_block(tower_data):
    """Return formatted provider-specific context for Crown Castle.

    This gets injected into the initial user message to give the agent
    relevant provider context before it starts making tool calls.
    """
    context = "PROVIDER CONTEXT (Crown Castle International):\n"
    context += "- National relationship: AT&T has 2,400+ leases with CCI\n"
    context += "- Master agreement: Renegotiated 2021, CPI+1%% escalation standard\n"
    context += "- Tower ID: %s\n" % tower_data.get("tower_id", "unknown")
    context += "- Current rate: $%s/month\n" % tower_data.get("current_monthly_rate", "N/A")
    context += "- Lease expiry: %s\n" % tower_data.get("lease_expiry", "N/A")

    years_remaining = tower_data.get("lease_years_remaining", None)
    if years_remaining is not None and years_remaining < 1.0:
        context += "- ⚠ LEASE EXPIRING SOON -- high urgency renegotiation\n"

    context += (
        "- CCI negotiation style: data-driven, responds to comparable market "
        "analysis, prefers multi-year commitments with escalation certainty\n"
    )
    return context
