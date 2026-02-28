"""
SBA Communications (SBAC) provider module.

Third largest US tower company. AT&T has ~1,800 leases with SBA nationally.
SBA is known for being the most aggressive on rate increases among the big three.
"""

# SBA acquired Mobilitie's tower assets in 2020 which added ~300 sites
# that AT&T leases from. Some of those sites still have legacy Mobilitie
# lease terms that are actually quite favorable -- don't renegotiate those
# unless they're expiring. See JIRA-1654.


def get_system_prompt(region):
    """Generate system prompt for SBA Communications negotiations."""
    prompt = (
        "You are an expert AT&T cell tower lease negotiator preparing a brief "
        "for renegotiating a lease with SBA Communications. "
        "AT&T maintains approximately 1,800 active tower leases with SBA nationally. "
        "SBA Communications is known as the most aggressive of the big three tower "
        "companies on rate increases and escalation terms. Their standard escalation "
        "is CPI+2%%, which is above market. "
        "Key leverage: AT&T has been actively shifting new deployments away from SBA "
        "toward Crown Castle and American Tower due to SBA's pricing. Reference this "
        "trend explicitly in negotiations. "
        "SBA responds to competitive pressure more than to data -- lead with "
        "AT&T's alternatives rather than comparable rate analysis."
    )

    if region == "northeast":
        prompt += " SBA has limited Northeast urban inventory compared to CCI and AMT."
    elif region == "southeast":
        prompt += " SBA has strong Southeast presence, especially in Florida where they are headquartered."
    elif region == "midwest":
        prompt += " SBA's Midwest footprint is the smallest of the big three, giving AT&T more leverage."
    elif region == "west":
        prompt += " SBA has been expanding in the West through acquisitions but is not yet established."

    return prompt


def get_context_block(tower_data):
    ctx = "PROVIDER CONTEXT (SBA Communications):\n"
    ctx += "- National relationship: AT&T has 1,800+ leases with SBAC\n"
    ctx += "- Standard escalation: CPI+2%% (above market -- negotiation target)\n"
    ctx += "- Tower ID: {tower_id}\n".format(tower_id=tower_data.get("tower_id", "unknown"))
    ctx += "- Current rate: ${rate}/month\n".format(rate=tower_data.get("current_monthly_rate", "N/A"))
    ctx += "- Lease expiry: {exp}\n".format(exp=tower_data.get("lease_expiry", "N/A"))

    if tower_data.get("lease_years_remaining", 99) < 1.0:
        ctx += "- ⚠ LEASE EXPIRING SOON -- high urgency renegotiation\n"

    ctx += "- SBAC negotiation style: aggressive pricing, responsive to competitive threats, less data-driven\n"
    return ctx
