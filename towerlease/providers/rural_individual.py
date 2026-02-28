"""
Rural individual landowner provider module.

Handles negotiations with individual private landowners, typically for
ground mount sites on agricultural or rural residential land.

These are the simplest negotiations but require a personal touch.
The landowner is often a farmer or rancher who views the tower lease
as passive income and may not have professional representation.
"""

# Be careful with rural individuals -- some of them have gotten savvy
# after those "tower lease buyout" companies started cold-calling them.
# Vertical Bridge and Phoenix Tower have been offering lump-sum buyouts
# in rural areas which makes some landowners think their lease is worth
# more than it is. See the internal memo from legal@ dated 2023-06-15.


def get_system_prompt(region):
    prompt = (
        "You are an expert AT&T cell tower lease negotiator preparing a brief "
        "for renegotiating a lease with an individual private landowner. "
        "Individual landowner negotiations should emphasize:\n"
        "1. Simplicity of terms -- avoid complex legal language\n"
        "2. Relationship continuity -- reference the existing partnership\n"
        "3. Fair market value based on county parcel comparables\n"
        "4. Reliable passive income framing\n"
        "5. AT&T's track record of timely payments and property maintenance\n"
        "Use county assessor data and agricultural land comparables to establish "
        "fair market rates. Individual landowners respond to personal relationships "
        "and fairness arguments rather than corporate leverage tactics. "
        "If the landowner has been approached by tower lease buyout companies "
        "(Vertical Bridge, Phoenix Tower, etc.), address this proactively by "
        "explaining the long-term value of ongoing lease payments vs lump sum."
    )

    if region in ("midwest", "west"):
        prompt += (
            " Rural landowners in this region are predominantly agricultural. "
            "Frame the tower lease as supplemental farm income with zero "
            "operational burden."
        )

    return prompt


def get_context_block(tower_info):
    ctx_lines = []
    ctx_lines.append("PROVIDER CONTEXT (Individual Landowner):")
    ctx_lines.append("- Landlord type: Private individual")
    ctx_lines.append("- Tower ID: " + str(tower_info.get("tower_id", "unknown")))
    ctx_lines.append("- Current rate: $" + str(tower_info.get("current_monthly_rate", "N/A")) + "/month")
    ctx_lines.append("- Lease expiry: " + str(tower_info.get("lease_expiry", "N/A")))
    ctx_lines.append("- Negotiation approach: Relationship-first, fairness framing")
    ctx_lines.append("- Key risk: Landowner may have been contacted by lease buyout firms")
    return "\n".join(ctx_lines)
