"""
Property lookup tool -- returns fake property record data for a given tower site.

This simulates a call to the internal AT&T property records API which pulls
from county assessor databases. In production this would hit the PropertyIQ
service but we're mocking it here because PropertyIQ is flaky and the team
doesn't want to deal with its auth flow in dev. See JIRA-1445.
"""
import hashlib
import random


# Fake owner names pool -- deliberately generic
_OWNER_NAMES = [
    "Johnson Family Trust",
    "Smith Holdings LLC",
    "Greenfield Properties Inc",
    "Martinez Land Co",
    "Heartland Realty Group",
    "Pacific Coast Ventures",
    "Blue Ridge Investments",
    "Cornerstone Property Management",
    "Oak Street Partners",
    "Riverside Development Corp",
    "Williams Agricultural Trust",
    "Sunset Ridge LLC",
    "Prairie Holdings Inc",
    "Mountain View Realty",
    "Coastal Land Partners",
]

_ZONING_CLASSES = [
    "C-2 (Commercial)",
    "I-1 (Light Industrial)",
    "R-3 (Residential Multi-family)",
    "AG (Agricultural)",
    "M-1 (Manufacturing)",
    "PUD (Planned Unit Development)",
    "MU (Mixed Use)",
]


def lookup(tower_id):
    """Look up property record for a tower site.

    Args:
        tower_id: AT&T tower identifier (e.g. ATT-TX-4821)

    Returns:
        dict with property record fields
    """
    # Use tower_id as seed for deterministic but varied results
    seed = int(hashlib.md5(tower_id.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    owner = rng.choice(_OWNER_NAMES)
    parcel_id = "%s-%s-%s" % (
        rng.randint(100, 999),
        rng.randint(1000, 9999),
        rng.randint(10, 99),
    )
    assessed_value = rng.randint(150000, 2500000)
    lot_acres = round(rng.uniform(0.25, 45.0), 2)
    zoning = rng.choice(_ZONING_CLASSES)

    return {
        "tower_id": tower_id,
        "owner_name": owner,
        "parcel_id": parcel_id,
        "assessed_value": assessed_value,
        "lot_size_acres": lot_acres,
        "zoning_classification": zoning,
        "county_record_url": "https://propertyiq.internal.att.com/parcel/%s" % parcel_id,
        "last_sale_date": "20%02d-%02d-%02d" % (
            rng.randint(10, 23),
            rng.randint(1, 12),
            rng.randint(1, 28),
        ),
        "last_sale_price": int(assessed_value * rng.uniform(0.8, 1.3)),
    }


TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "property_lookup",
        "description": (
            "Look up property records for a tower site including owner information, "
            "parcel details, assessed value, lot size, and zoning classification. "
            "Use this to understand the property context for lease negotiations."
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
    },
}
