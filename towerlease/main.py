"""
CLI entrypoint for TowerLease Intelligence.

Retained from the original pre-FastAPI version when this was a CLI-only tool.
Still useful for quick testing and demos without spinning up the server.

Usage:
    python -m towerlease.main --tower ATT-TX-4821 --provider crown_castle --region southeast
"""
import os
import sys
import json
import argparse

from dotenv import load_dotenv

load_dotenv()

from towerlease.agents.negotiation_agent import run_negotiation_agent
from towerlease.agents.brief_generator import generate_brief


def main():
    parser = argparse.ArgumentParser(
        description="TowerLease Intelligence -- CLI negotiation brief generator"
    )
    parser.add_argument("--tower", required=True, help="Tower ID (e.g. ATT-TX-4821)")
    parser.add_argument(
        "--provider",
        required=True,
        choices=["crown_castle", "american_tower", "sba_communications", "municipal", "rural_individual"],
        help="Tower provider/landlord type",
    )
    parser.add_argument(
        "--region",
        required=True,
        choices=["northeast", "southeast", "midwest", "west"],
    )
    parser.add_argument("--rate", type=int, default=3000, help="Current monthly rate in dollars")
    parser.add_argument("--expiry", default="2025-08-01", help="Lease expiry date (YYYY-MM-DD)")
    parser.add_argument("--years-remaining", type=float, default=0.5, help="Years remaining on lease")

    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable not set.")
        print("Set it in .env or export it before running.")
        sys.exit(1)

    lease_data = {
        "tower_id": args.tower,
        "current_monthly_rate": args.rate,
        "lease_expiry": args.expiry,
        "lease_years_remaining": args.years_remaining,
    }

    print("=" * 60)
    print("TowerLease Intelligence -- Negotiation Brief Generator")
    print("=" * 60)
    print("Tower: %s" % args.tower)
    print("Provider: %s" % args.provider)
    print("Region: %s" % args.region)
    print("Current Rate: $%d/mo" % args.rate)
    print("Lease Expiry: %s" % args.expiry)
    print("-" * 60)
    print("Running negotiation agent...\n")

    raw_analysis, messages = run_negotiation_agent(
        tower_id=args.tower,
        lease_data=lease_data,
        provider=args.provider,
        region=args.region,
    )

    print("Agent complete. Generating structured brief...\n")

    brief = generate_brief(raw_analysis, lease_data)

    print("=" * 60)
    print("NEGOTIATION BRIEF")
    print("=" * 60)
    print(json.dumps(brief, indent=2))


if __name__ == "__main__":
    main()
