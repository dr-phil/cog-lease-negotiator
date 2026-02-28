"""
Northeast region market data and benchmarks.

Covers: NY, NJ, CT, MA, PA, NH, VT, ME, RI
Last updated by jcrawford@ after Q4 2023 rate survey.
"""

# NOTE: These rates were validated against the 2023 Q4 CoStar tower lease
# comps pull. The rooftop numbers jumped ~18% YoY in Manhattan/Boston metro
# due to 5G densification pressure. See JIRA-1847 for the full analysis.

BENCHMARK_RATES = {
    "rooftop": {"low": 12000, "median": 18000, "high": 28000},
    "ground_mount": {"low": 2200, "median": 3400, "high": 5000},
    "water_tower": {"low": 3800, "median": 5500, "high": 8000},
    "monopole": {"low": 2800, "median": 4200, "high": 6200},
}


def get_market_context():
    """Return narrative market context for the Northeast region."""
    return (
        "The Northeast corridor represents AT&T's highest-density urban tower "
        "market. Rooftop installations in Manhattan, Boston, and Philadelphia "
        "command premium rates due to extreme site scarcity and zoning complexity. "
        "Building owners in these markets are sophisticated and often represented "
        "by specialized telecom lease consultants. The region has seen a 15-20%% "
        "rate increase over the past two years driven by 5G small cell backhaul "
        "demand and carrier densification strategies. Municipal permitting in "
        "Connecticut and New Jersey adds 4-6 months to new site timelines, "
        "which increases the value of existing lease renewals. Ground mount sites "
        "in suburban NJ and PA remain comparatively affordable but are increasingly "
        "contested by T-Mobile and Dish Network buildouts."
    )


# Old logic from before the 2022 rate normalization -- keeping for reference
# in case finance asks about the methodology change again.
#
# def get_market_context_v1():
#     """Original market context that used flat regional multipliers."""
#     base_text = "Northeast market rates are {mult}x the national average"
#     if _is_metro_area(tower_data.get("zip", "")):
#         mult = 2.4
#     else:
#         mult = 1.6
#     return base_text.format(mult=mult)
#
# def _is_metro_area(zip_code):
#     # Hardcoded zip prefixes for NYC, BOS, PHL
#     metro_prefixes = ["100", "101", "102", "021", "022", "191"]
#     return any(zip_code.startswith(p) for p in metro_prefixes)
