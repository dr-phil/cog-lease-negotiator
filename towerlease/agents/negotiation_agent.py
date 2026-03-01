"""
Core negotiation agent loop.

This is the main agentic loop that drives the negotiation brief generation.
It uses the old openai SDK pattern (pre-1.0) with manual function call parsing.

The agent makes multiple tool calls to gather context before synthesizing
a negotiation brief. Typical flow:
  1. property_lookup -- get property context
  2. lease_comparables -- get market rate benchmarks
  3. tower_utilization OR regulatory_lookup -- depending on provider type

Originally written by dkim@ in 2023-Q1, refactored by jcrawford@ in 2023-Q3
to add the provider/region system prompt injection.
"""
import json
import importlib

from openai import OpenAI

from towerlease.tools import property_lookup
from towerlease.tools import lease_comparables
from towerlease.tools import tower_utilization
from towerlease.tools import regulatory_lookup
from towerlease.services import lease_history_service
from towerlease.services import negotiation_notes_service

# Lazy-initialized client; created on first use so that tests can patch
# the module-level `client` attribute before any real calls are made.
client = None


def _get_client():
    global client
    if client is None:
        client = OpenAI()
    return client

# Tool definitions wrapped for the Responses API tools format
TOOL_DEFINITIONS = [
    {"type": "function", "function": property_lookup.TOOL_DEFINITION},
    {"type": "function", "function": lease_comparables.TOOL_DEFINITION},
    {"type": "function", "function": tower_utilization.TOOL_DEFINITION},
    {"type": "function", "function": regulatory_lookup.TOOL_DEFINITION},
    {"type": "function", "function": lease_history_service.TOOL_DEFINITION},
    {"type": "function", "function": negotiation_notes_service.TOOL_DEFINITION},
]

# Map function names to their implementation
_TOOL_DISPATCH = {
    "property_lookup": property_lookup.lookup,
    "lease_comparables": lease_comparables.lookup,
    "tower_utilization": tower_utilization.lookup,
    "regulatory_lookup": regulatory_lookup.lookup,
    "get_lease_history": lease_history_service.get_lease_history,
    "get_negotiation_notes": negotiation_notes_service.get_negotiation_notes,
}


def dispatch_tool(fn_name, fn_args):
    """Dispatch a tool call to the appropriate function.

    Args:
        fn_name: name of the function to call
        fn_args: dict of arguments parsed from the model response

    Returns:
        dict result from the tool function
    """
    handler = _TOOL_DISPATCH.get(fn_name)
    if handler is None:
        return {"error": "Unknown tool: %s" % fn_name}
    try:
        return handler(**fn_args)
    except TypeError as e:
        # This happens sometimes when the model passes unexpected args.
        # We just return the error and let the model recover.
        return {"error": "Tool call failed: %s" % str(e)}


def _load_provider_module(provider):
    """Dynamically load a provider module."""
    return importlib.import_module("towerlease.providers.%s" % provider)


def _load_region_module(region):
    return importlib.import_module("towerlease.regions.%s" % region)


def build_system_prompt(provider, region):
    """Construct the system prompt by combining provider and region context.

    The system prompt is assembled from:
    1. Provider-specific negotiation guidance
    2. Region market context
    """
    provider_mod = _load_provider_module(provider)
    region_mod = _load_region_module(region)

    provider_prompt = provider_mod.get_system_prompt(region)
    market_context = region_mod.get_market_context()

    system_prompt = provider_prompt + "\n\nREGION MARKET CONTEXT:\n" + market_context

    system_prompt += (
        "\n\nINSTRUCTIONS:\n"
        "1. First, call get_lease_history to retrieve AT&T's internal negotiation "
        "history for this tower. This gives you historical context on past rates, "
        "escalation patterns, and negotiator notes.\n"
        "2. Call get_negotiation_notes to pull relationship intelligence from the "
        "CRM for this provider. Understand known sticking points and committed "
        "positions before analyzing external data.\n"
        "3. Look up the property record for this tower site.\n"
        "4. Then, pull comparable lease rates for this region and tower type. Use "
        "the internal history from steps 1-2 to contextualize the market data.\n"
        "5. Check tower utilization data to assess leverage position.\n"
        "6. If the provider is municipal or the region has complex permitting, "
        "also check regulatory context.\n"
        "7. Synthesize all gathered data into a comprehensive negotiation brief.\n"
        "8. Include specific rate recommendations with supporting evidence.\n"
        "Always call get_lease_history and get_negotiation_notes before the market "
        "comparables tools. Internal history should inform how you interpret "
        "external market data.\n"
        "Always make your tool calls before providing your final analysis."
    )

    return system_prompt


def build_initial_message(tower_id, lease_data, provider, region):
    """Build the initial user message with tower data and provider context."""
    provider_mod = _load_provider_module(provider)
    context_block = provider_mod.get_context_block(lease_data)

    msg = "Please prepare a negotiation brief for the following tower lease renewal:\n\n"
    msg += "Tower ID: %s\n" % tower_id
    msg += "Current Monthly Rate: $%s\n" % lease_data.get("current_monthly_rate", "N/A")
    msg += "Lease Expiry: %s\n" % lease_data.get("lease_expiry", "N/A")
    msg += "Years Remaining: %s\n" % lease_data.get("lease_years_remaining", "N/A")
    msg += "\n" + context_block

    return msg


def run_negotiation_agent(tower_id, lease_data, provider, region):
    """Execute the full negotiation agent loop.

    This function runs a while loop that continues making ChatCompletion
    calls until the model returns a final response (finish_reason == "stop").
    The model can make function calls which are dispatched to mock tools
    and the results fed back into the conversation.

    Args:
        tower_id: AT&T tower identifier
        lease_data: dict with current lease terms
        provider: provider identifier string
        region: region identifier string

    Returns:
        tuple of (final_response_text, response_id)
    """
    system_prompt = build_system_prompt(provider, region)

    # Seed the conversation with the Responses API
    response = _get_client().responses.create(
        model="gpt-4",
        instructions=system_prompt,
        input=build_initial_message(tower_id, lease_data, provider, region),
        tools=TOOL_DEFINITIONS,
        store=True,
    )

    # Agent loop -- keep calling until we get a stop response
    max_iterations = 10  # safety valve, shouldn't need more than 5-6
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        tool_calls = [item for item in response.output if item.type == "function_call"]
        if not tool_calls:
            return response.output_text, response.id

        tool_outputs = []
        for tc in tool_calls:
            result = dispatch_tool(tc.name, json.loads(tc.arguments))
            tool_outputs.append({
                "type": "function_call_output",
                "call_id": tc.call_id,
                "output": json.dumps(result),
            })

        response = _get_client().responses.create(
            model="gpt-4",
            previous_response_id=response.id,
            input=tool_outputs,
            tools=TOOL_DEFINITIONS,
            store=True,
        )

    # If we hit max iterations, return whatever we have
    # This shouldn't happen in practice but better than infinite loop
    return response.output_text, response.id
