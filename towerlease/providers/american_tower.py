"""
American Tower Corporation (AMT) provider module.

Second largest tower company in the US. AT&T has ~2,100 active leases nationally.
AMT tends to be more aggressive on escalation clauses than Crown Castle.
"""

# American Tower's standard contract template changed in mid-2022.
# The new template includes a 5-year rate reset clause that wasn't in
# older agreements. See confluence: tower-leasing/amt-contract-template-2022


def get_system_prompt(region):
    base = (
        "You are an expert AT&T cell tower lease negotiator preparing a brief "
        "for renegotiating a lease with American Tower Corporation (AMT). "
        "AT&T holds approximately 2,100 active tower leases with American Tower, "
        "representing significant portfolio leverage. "
        "AMT has historically been more aggressive than Crown Castle on escalation "
        "terms -- their standard is CPI+1.5%% vs Crown Castle's CPI+1%%. "
        "Use Crown Castle's more favorable terms as a benchmark in negotiations. "
        "AMT responds well to long-term commitment offers (10+ year extensions) "
        "in exchange for rate concessions. "
        "Emphasize AT&T's consolidation strategy and willingness to shift volume "
        "to competitors if rates are not competitive."
    )

    region_addendum = {
        "northeast": (
            " AMT has strong Northeast urban inventory, particularly in "
            "the NYC metro and Boston corridor. Their rooftop sites here "
            "are premium-priced but negotiable given AT&T volume."
        ),
        "southeast": (
            " AMT is the dominant tower company in Florida and has been "
            "expanding aggressively in the Carolinas. Competition with "
            "SBA in these markets can be leveraged."
        ),
        "midwest": (
            " AMT has been acquiring smaller regional tower portfolios "
            "in the Midwest. Recently acquired sites may have legacy "
            "lease terms that are favorable to renegotiate."
        ),
        "west": (
            " AMT has significant California inventory. Their permitting "
            "relationships are less established than Crown Castle's in "
            "this region, which may create flexibility on pricing."
        ),
    }

    base += region_addendum.get(region, "")
    return base


def get_context_block(tower_info):
    """Build provider context block for American Tower negotiations."""
    lines = [
        "PROVIDER CONTEXT (American Tower Corporation):",
        "- National relationship: AT&T has 2,100+ leases with AMT",
        "- Standard escalation: CPI+1.5% (higher than CCI benchmark)",
        "- Tower ID: {}".format(tower_info.get("tower_id", "unknown")),
        "- Current rate: ${}/month".format(tower_info.get("current_monthly_rate", "N/A")),
        "- Lease expiry: {}".format(tower_info.get("lease_expiry", "N/A")),
    ]

    years_left = tower_info.get("lease_years_remaining", None)
    if years_left is not None and years_left < 1.0:
        lines.append("- ⚠ LEASE EXPIRING SOON -- high urgency renegotiation")

    lines.append(
        "- AMT negotiation style: aggressive on escalation, open to "
        "long-term commitment trades, responds to competitive pressure"
    )
    return "\n".join(lines)
