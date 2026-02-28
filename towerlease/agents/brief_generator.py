"""
Brief generator module.

Takes the raw agent output from the negotiation agent and formats it into
the structured JSON response shape expected by the API.

This is deliberately a separate ChatCompletion call rather than doing it
in one shot. The original design had the negotiation agent return unstructured
text and this module was added later to impose structure. Classic organic
growth pattern -- works fine, just a bit wasteful on tokens.

# TODO: consider merging this back into the negotiation agent with a
# structured output format. But it works and nobody's complained about
# the extra latency so... JIRA-2150 (backlog, low priority)
"""
import os
import json

import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


_FORMATTING_PROMPT = """You are a formatting assistant for AT&T's tower lease negotiation system.

Take the raw negotiation analysis provided and extract/format it into a structured JSON response.

The JSON must have exactly these fields:
{
  "brief": "A 2-3 paragraph executive summary of the negotiation position",
  "recommended_opening_rate": <integer, the rate AT&T should open negotiations with>,
  "walk_away_rate": <integer, the maximum rate AT&T should accept>,
  "key_leverage_points": ["point 1", "point 2", ...],
  "comparable_rates": {
    "low": <integer>,
    "median": <integer>,
    "high": <integer>
  },
  "provider_context": "Summary of provider-specific considerations",
  "region_context": "Summary of regional market conditions"
}

IMPORTANT: Return ONLY valid JSON, no markdown formatting or code blocks. The recommended_opening_rate should be below the current rate (we're trying to negotiate DOWN). The walk_away_rate should be at or slightly below the current rate."""


def generate_brief(raw_analysis, tower_data):
    """Generate a structured brief from raw agent analysis.

    Args:
        raw_analysis: unstructured text from the negotiation agent
        tower_data: dict with tower/lease information for context

    Returns:
        dict with structured brief fields
    """
    current_rate = tower_data.get("current_monthly_rate", 3000)

    user_msg = (
        "Raw negotiation analysis:\n\n%s\n\n"
        "Current monthly rate: $%d\n"
        "Format this into the required JSON structure."
        % (raw_analysis, current_rate)
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": _FORMATTING_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.2,  # low temp for structured output
    )

    content = response["choices"][0]["message"]["content"]

    try:
        brief_data = json.loads(content)
    except json.JSONDecodeError:
        # Sometimes the model wraps the JSON in markdown code blocks
        # despite being told not to. Strip them and try again.
        cleaned = content.strip()
        if cleaned.startswith("```"):
            # Remove first and last lines (```json and ```)
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1])
        try:
            brief_data = json.loads(cleaned)
        except json.JSONDecodeError:
            # Last resort -- return a default structure
            # This has only happened twice in production (JIRA-1967)
            brief_data = _build_fallback_brief(raw_analysis, current_rate)

    # Validate and fill in any missing fields
    brief_data = _ensure_complete(brief_data, current_rate)
    return brief_data


def _ensure_complete(brief_data, current_rate):
    """Make sure all required fields are present."""
    defaults = {
        "brief": brief_data.get("brief", "Analysis complete. See details below."),
        "recommended_opening_rate": brief_data.get("recommended_opening_rate", int(current_rate * 0.85)),
        "walk_away_rate": brief_data.get("walk_away_rate", int(current_rate * 0.97)),
        "key_leverage_points": brief_data.get("key_leverage_points", ["Market rate analysis pending"]),
        "comparable_rates": brief_data.get("comparable_rates", {
            "low": int(current_rate * 0.75),
            "median": int(current_rate * 0.95),
            "high": int(current_rate * 1.2),
        }),
        "provider_context": brief_data.get("provider_context", "Provider context not available"),
        "region_context": brief_data.get("region_context", "Region context not available"),
    }
    return defaults


def _build_fallback_brief(raw_analysis, current_rate):
    """Build a fallback brief when JSON parsing fails entirely."""
    return {
        "brief": raw_analysis[:500] if raw_analysis else "Brief generation failed",
        "recommended_opening_rate": int(current_rate * 0.85),
        "walk_away_rate": int(current_rate * 0.97),
        "key_leverage_points": [
            "Unable to parse structured leverage points",
            "Review raw analysis for details",
        ],
        "comparable_rates": {
            "low": int(current_rate * 0.75),
            "median": int(current_rate * 0.95),
            "high": int(current_rate * 1.2),
        },
        "provider_context": "Parse error -- see raw brief text",
        "region_context": "Parse error -- see raw brief text",
    }
