"""
Tower utilization tool.

Returns mock utilization data for a given tower including current tenants,
available capacity, and bandwidth utilization. Higher utilization = more
leverage for AT&T since the tower owner benefits from multi-tenant revenue.

The real version of this hits the NMS (Network Management System) API.
"""
import hashlib
import random


_CARRIER_NAMES = [
    "T-Mobile",
    "Verizon Wireless",
    "Dish Network",
    "US Cellular",
    "Charter Communications",
]

_EQUIPMENT_TYPES = [
    "4G LTE panel antenna",
    "5G NR massive MIMO",
    "5G mmWave small cell",
    "Microwave backhaul dish",
    "4G LTE + 5G combo panel",
]


def lookup(tower_id):
    """Get utilization data for a tower.

    Args:
        tower_id: AT&T tower identifier

    Returns:
        dict with utilization metrics and tenant information
    """
    seed = int(hashlib.md5(tower_id.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    # AT&T is always a tenant
    tenants = [
        {
            "carrier": "AT&T",
            "equipment": rng.choice(_EQUIPMENT_TYPES),
            "lease_position": "primary",
            "since": "20%02d" % rng.randint(8, 18),
        }
    ]

    # Add 1-2 other tenants
    num_other = rng.randint(1, 2)
    other_carriers = rng.sample(_CARRIER_NAMES, num_other)
    for carrier in other_carriers:
        tenants.append({
            "carrier": carrier,
            "equipment": rng.choice(_EQUIPMENT_TYPES),
            "lease_position": "co-tenant",
            "since": "20%02d" % rng.randint(12, 23),
        })

    total_capacity_slots = rng.choice([4, 5, 6, 8])
    occupied_slots = len(tenants)
    available_slots = total_capacity_slots - occupied_slots
    bandwidth_pct = rng.randint(35, 92)

    return {
        "tower_id": tower_id,
        "total_tenant_slots": total_capacity_slots,
        "occupied_slots": occupied_slots,
        "available_slots": available_slots,
        "tenants": tenants,
        "bandwidth_utilization_pct": bandwidth_pct,
        "structural_capacity_remaining_pct": rng.randint(20, 70),
        "last_structural_inspection": "20%02d-%02d-01" % (
            rng.randint(21, 24),
            rng.randint(1, 12),
        ),
        # higher multi-tenant count = more leverage for AT&T
        "leverage_note": (
            "Tower has %d of %d slots occupied. "
            % (occupied_slots, total_capacity_slots)
            + ("High occupancy increases AT&T leverage -- tower owner "
               "depends on multi-tenant revenue."
               if occupied_slots >= 3
               else "Moderate occupancy -- tower owner may seek to "
               "attract additional tenants which gives AT&T some leverage.")
        ),
    }


TOOL_DEFINITION = {
    "name": "tower_utilization",
    "description": (
        "Get current utilization data for a tower including tenant list, "
        "capacity metrics, and bandwidth utilization. Use this to assess "
        "AT&T's leverage position -- higher utilization means the tower owner "
        "depends more on existing tenant revenue."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "tower_id": {
                "type": "string",
                "description": "The AT&T tower identifier (e.g. ATT-TX-4821)",
            }
        },
        "required": ["tower_id"],
    },
}
