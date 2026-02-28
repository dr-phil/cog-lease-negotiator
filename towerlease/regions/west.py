"""
West region market data and benchmarks.

Covers: CA, OR, WA, AZ, NV, UT, CO, NM, MT, WY, ID, HI, AK
"""

# The west region is a mess because it covers everything from downtown SF
# to rural Montana. The benchmark rates here are averaged across the whole
# region which makes them less useful for individual negotiations. The
# system prompt logic in the providers tries to compensate for this.
# TODO: split into West Coast and Mountain sub-regions -- JIRA-2087

BENCHMARK_RATES = {
    "rooftop": {"low": 10000, "median": 16000, "high": 25000},
    "ground_mount": {"low": 2000, "median": 3000, "high": 4500},
    "water_tower": {"low": 3200, "median": 4800, "high": 7000},
    "monopole": {"low": 2400, "median": 3800, "high": 5600},
}


def get_market_context():
    return ("The West region presents unique challenges due to environmental "
            "review requirements under CEQA (California) and SEPA (Washington). "
            "New tower siting in California can take 12-18 months due to "
            "environmental impact review, making existing lease renewals "
            "significantly more valuable to AT&T. Rooftop rates in San Francisco, "
            "Los Angeles, and Seattle rival Northeast urban markets. Colorado "
            "and Arizona have seen rapid suburban growth creating new tower "
            "demand that landlords are leveraging for higher rates. Rural sites "
            "in Montana, Wyoming, and Idaho remain affordable but face "
            "infrastructure access challenges. The region has active tribal "
            "land considerations in New Mexico and Arizona that require "
            "specialized negotiation approaches. Hawaii and Alaska sites "
            "command premium rates due to logistical complexity and limited "
            "alternatives.")
