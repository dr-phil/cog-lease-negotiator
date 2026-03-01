"""
Lease comparables tool.

Returns comparable tower lease data for a given region and tower type.
In production this would query the LeaseComp database maintained by
the tower leasing analytics team. The mock version pulls from region
benchmark rates and applies random variance.

Last refactored by mwilliams@ in 2023-Q2 to add provider filtering.
"""
import hashlib
import random
import importlib


def _get_region_benchmarks(region):
    """Dynamically load benchmark rates for a region."""
    mod = importlib.import_module("towerlease.regions.%s" % region)
    return mod.BENCHMARK_RATES


def _generate_comp_address(rng):
    streets = [
        "Oak Hill Rd", "Industrial Blvd", "Route 9", "County Road 42",
        "Main St", "Tower Lane", "Hilltop Dr", "Airport Rd",
        "Commerce Way", "Farm Road 1120", "State Highway 35",
        "Broadview Ave", "Wireless Way", "Signal Hill Rd",
    ]
    return "%d %s" % (rng.randint(100, 9999), rng.choice(streets))


def _generate_escalation(rng):
    """Generate a realistic escalation clause description."""
    options = [
        "3% annual fixed",
        "CPI + 1%",
        "CPI + 1.5%",
        "CPI + 2%",
        "2.5% annual fixed",
        "CPI (capped at 3%)",
        "4% annual fixed",  # old legacy terms
    ]
    return rng.choice(options)


def lookup(region, tower_type, provider=None):
    """Find comparable tower leases in the same region and tower type.

    Args:
        region: one of northeast, southeast, midwest, west
        tower_type: one of rooftop, ground_mount, water_tower, monopole
        provider: optional provider filter

    Returns:
        list of 5 comparable lease records
    """
    benchmarks = _get_region_benchmarks(region)

    if tower_type not in benchmarks:
        # fallback -- shouldn't happen but the old code had this guard
        tower_type = "ground_mount"

    rates = benchmarks[tower_type]
    seed_str = "%s-%s-%s" % (region, tower_type, provider or "all")
    seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    comps = []
    for i in range(5):
        # Generate rate with variance around median
        base_rate = rng.randint(rates["low"], rates["high"])
        # Apply some noise
        noise = rng.uniform(-0.08, 0.08)
        monthly_rate = int(base_rate * (1 + noise))

        comp = {
            "comp_id": "COMP-%s-%04d" % (region[:2].upper(), rng.randint(1000, 9999)),
            "address": _generate_comp_address(rng),
            "distance_miles": round(rng.uniform(0.5, 25.0), 1),
            "monthly_rate": monthly_rate,
            "tower_type": tower_type,
            "lease_date": "20%02d-%02d-01" % (rng.randint(19, 24), rng.randint(1, 12)),
            "escalation_terms": _generate_escalation(rng),
            "provider": provider or rng.choice(["crown_castle", "american_tower", "sba_communications"]),
            "lease_term_years": rng.choice([5, 7, 10, 15]),
        }
        comps.append(comp)

    # Sort by distance for readability
    comps.sort(key=lambda c: c["distance_miles"])
    return comps


TOOL_DEFINITION = {
    "type": "function",
    "name": "lease_comparables",
    "description": (
        "Find comparable tower lease rates in the same region and for the same "
        "tower type. Returns 5 comparable leases with monthly rates, distances, "
        "lease dates, and escalation terms. Use this to establish market rate "
        "benchmarks for negotiation."
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
            "provider": {
                "type": "string",
                "description": "Optional provider filter: crown_castle, american_tower, sba_communications, municipal, or rural_individual",
            },
        },
        "required": ["region", "tower_type"],
    },
}
