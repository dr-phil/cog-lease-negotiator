"""
Test fixtures for TowerLease Intelligence.

Mocks the OpenAI Responses API (client.responses.create) for the negotiation
agent, and openai.ChatCompletion.create for the brief generator and follow-up
agent (which have not yet been migrated).

Two negotiation agent fixtures:
  - mock_openai_single_turn: returns a stop response directly (no tool calls)
  - mock_openai_with_tool_call: simulates a tool call loop then stop
"""
import json
import pytest
from unittest.mock import patch, MagicMock

from towerlease.server import session_store


@pytest.fixture(autouse=True)
def clear_sessions():
    """Clear session store between tests."""
    session_store.clear_all()
    yield
    session_store.clear_all()


def _make_function_call_item(fn_name, fn_args, call_id):
    """Build a mock output item of type 'function_call'."""
    item = MagicMock()
    item.type = "function_call"
    item.name = fn_name
    item.arguments = json.dumps(fn_args) if isinstance(fn_args, dict) else fn_args
    item.call_id = call_id
    return item


def _make_text_output_item(text):
    """Build a mock output item of type 'message' (not function_call)."""
    item = MagicMock()
    item.type = "message"
    item.content = text
    return item


def _make_responses_api_response(output_items, output_text=None, response_id=None):
    """Build a mock Responses API response object.

    Args:
        output_items: list of mock output items (function_call or message)
        output_text: the .output_text string (for stop/text responses)
        response_id: the .id string for this response
    """
    response = MagicMock()
    response.output = output_items
    response.output_text = output_text or ""
    response.id = response_id or "resp_mock_default"
    return response


@pytest.fixture
def mock_openai_single_turn():
    """Mock that returns a stop response on the first call (no tool calls).

    Used for negotiation agent tests where the agent completes in one turn.
    The brief generator still uses the old ChatCompletion API so it gets
    its own separate patch.
    """
    mock_brief_json = json.dumps({
        "brief": "Mock negotiation brief for testing.",
        "recommended_opening_rate": 2800,
        "walk_away_rate": 3100,
        "key_leverage_points": [
            "AT&T portfolio leverage with 2000+ national leases",
            "Current rate above regional median",
            "Lease expiring soon gives urgency to both parties",
        ],
        "comparable_rates": {"low": 2600, "median": 3000, "high": 3800},
        "provider_context": "Mock provider context for testing.",
        "region_context": "Mock region context for testing.",
    })

    # Mock the Responses API for the negotiation agent
    agent_response = _make_responses_api_response(
        output_items=[_make_text_output_item("Raw analysis: rates are above market median.")],
        output_text="Raw analysis: rates are above market median.",
        response_id="resp_single_turn_001",
    )

    mock_client = MagicMock()
    mock_client.responses.create.return_value = agent_response

    with patch("towerlease.agents.negotiation_agent._get_client", return_value=mock_client), \
         patch("openai.ChatCompletion.create") as mock_chat:

        # Brief generator still uses old API
        mock_chat.return_value = _build_chat_response("stop", content=mock_brief_json)

        yield mock_client, mock_chat


@pytest.fixture
def mock_openai_with_tool_call():
    """Mock that simulates a tool call loop via the Responses API.

    Call sequence:
    1. Initial call returns function_call to get_lease_history
    2. Second call returns function_call to get_negotiation_notes
    3. Third call returns function_call to lease_comparables
    4. Fourth call returns stop with final analysis

    The brief generator (5th call) still uses the old ChatCompletion API.
    """
    mock_brief_json = json.dumps({
        "brief": "Comprehensive mock brief after tool calls.",
        "recommended_opening_rate": 2700,
        "walk_away_rate": 3050,
        "key_leverage_points": [
            "Comparable rates show current lease is 15% above median",
            "Tower utilization at 75% -- multi-tenant leverage",
            "Property assessed value supports lower rate",
        ],
        "comparable_rates": {"low": 2400, "median": 2900, "high": 3600},
        "provider_context": "Provider responds to data-driven arguments.",
        "region_context": "Regional rates trending down for this tower type.",
        "negotiation_history_summary": "Historical rates show consistent 4-5% annual escalation. Last negotiated in 2022.",
        "crm_intelligence": "SBA Communications is a preferred-tier provider. Account team restructured in Q4 2023.",
    })

    # Build the sequence of Responses API responses for the agent loop
    responses_sequence = [
        # Call 1: agent retrieves internal lease history first
        _make_responses_api_response(
            output_items=[_make_function_call_item("get_lease_history", {"tower_id": "ATT-FL-4205"}, "call_001")],
            response_id="resp_tool_001",
        ),
        # Call 2: agent retrieves CRM negotiation notes
        _make_responses_api_response(
            output_items=[_make_function_call_item("get_negotiation_notes", {"provider": "sba_communications"}, "call_002")],
            response_id="resp_tool_002",
        ),
        # Call 3: agent pulls market comparables
        _make_responses_api_response(
            output_items=[_make_function_call_item("lease_comparables", {"region": "southeast", "tower_type": "ground_mount"}, "call_003")],
            response_id="resp_tool_003",
        ),
        # Call 4: agent returns final analysis (no tool calls)
        _make_responses_api_response(
            output_items=[_make_text_output_item(
                "Based on internal lease history, CRM intelligence, and comparable analysis, "
                "the current rate of $3200/mo is above the regional median of $2800. "
                "AT&T has strong leverage due to multi-tenant occupancy."
            )],
            output_text=(
                "Based on internal lease history, CRM intelligence, and comparable analysis, "
                "the current rate of $3200/mo is above the regional median of $2800. "
                "AT&T has strong leverage due to multi-tenant occupancy."
            ),
            response_id="resp_final_004",
        ),
    ]

    mock_client = MagicMock()
    mock_client.responses.create.side_effect = responses_sequence

    with patch("towerlease.agents.negotiation_agent._get_client", return_value=mock_client), \
         patch("openai.ChatCompletion.create") as mock_chat:

        # Brief generator still uses old API
        mock_chat.return_value = _build_chat_response("stop", content=mock_brief_json)

        yield mock_client, mock_chat


@pytest.fixture
def mock_openai_followup():
    """Mock for follow-up agent tests (still uses old ChatCompletion API)."""
    with patch("openai.ChatCompletion.create") as mock_create:
        mock_create.return_value = _build_chat_response(
            "stop",
            content="If they push back on comparables, reference the post-2021 Crown Castle master agreement rates.",
        )
        yield mock_create


def _build_chat_response(finish_reason, content=None, fn_name=None, fn_args=None):
    """Helper to build a properly structured mock ChatCompletion response dict.

    Used for the brief generator and follow-up agent which still use the
    old ChatCompletion API.
    """
    message = {"role": "assistant"}

    if finish_reason == "function_call":
        message["content"] = None
        message["function_call"] = {
            "name": fn_name,
            "arguments": json.dumps(fn_args) if fn_args else "{}",
        }
    else:
        message["content"] = content or ""

    return {
        "choices": [
            {
                "message": message,
                "finish_reason": finish_reason,
            }
        ]
    }
