"""
Southeast region market data and benchmarks.

Covers: FL, GA, NC, SC, VA, TN, AL, MS, LA, AR
"""

# TODO: break Florida out into its own sub-region -- the Miami/Tampa corridor
# has completely different dynamics than rural AL/MS. See JIRA-1923.

BENCHMARK_RATES = {
    "rooftop": {"low": 8000, "median": 13000, "high": 20000},
    "ground_mount": {"low": 1800, "median": 2800, "high": 4200},
    "water_tower": {"low": 3000, "median": 4500, "high": 6500},
    "monopole": {"low": 2200, "median": 3400, "high": 5000},
}


def get_market_context():
    return (
        "The Southeast is AT&T's most active 5G buildout region, which has "
        "shifted landlord leverage significantly over the past 18 months. "
        "Tower owners in Florida and Georgia metro areas are increasingly "
        "aware of carrier demand and are pushing for higher escalation rates. "
        "Charlotte, Atlanta, and Nashville have seen particularly aggressive "
        "rate increases on rooftop sites. Rural ground mount sites in Alabama, "
        "Mississippi, and Arkansas remain favorable for AT&T due to limited "
        "carrier competition and abundant land availability. Hurricane risk "
        "in coastal areas creates maintenance cost considerations that can "
        "be used as negotiation leverage. The region has relatively permissive "
        "tower siting regulations compared to the Northeast, reducing new-build "
        "alternatives cost and timeline."
    )
