"""
Midwest region market data and benchmarks.

Covers: OH, MI, IN, IL, WI, MN, IA, MO, KS, NE, ND, SD
Last reviewed: 2023-Q3 by the tower leasing team.
"""

BENCHMARK_RATES = {
    "rooftop": {"low": 6000, "median": 9500, "high": 15000},
    "ground_mount": {"low": 1200, "median": 2000, "high": 3200},
    "water_tower": {"low": 2000, "median": 3200, "high": 4800},
    "monopole": {"low": 1600, "median": 2600, "high": 3800},
}


def get_market_context():
    """Market context for Midwest region.

    The Midwest has the most favorable rate environment for AT&T
    across all four operating regions.
    """
    ctx = (
        "The Midwest represents AT&T's most cost-effective tower market. "
        "Rural ground mount sites are abundant and landowner expectations "
        "are generally aligned with historical AT&T rate ranges. Chicago "
        "metro rooftop sites are the exception -- they command rates closer "
        "to Northeast levels due to building density and zoning restrictions. "
        "Agricultural land in Iowa, Kansas, and Nebraska provides low-cost "
        "ground mount alternatives that can be referenced in negotiations. "
        "Water tower installations are common in small towns across Ohio "
        "and Indiana where municipalities are receptive to lease revenue. "
        "The region has minimal permitting friction for ground mount sites, "
        "with typical approval timelines of 60-90 days. Carrier competition "
        "is moderate -- T-Mobile has been expanding but Verizon presence "
        "outside major metros is limited."
    )
    return ctx
