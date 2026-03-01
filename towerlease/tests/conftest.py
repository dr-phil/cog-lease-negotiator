"""
Test fixtures for TowerLease Intelligence.

Mocks client.responses.create to avoid hitting the real API in tests.
Two fixtures:
  - mock_openai_single_turn: returns a stop response directly
  - mock_openai_with_tool_call: simulates a tool call loop (function_call then stop)
"""
import json
import pytest
from unittest.mock import patch, MagicMock

from towerlease.server import session_store
from towerlease.agents import negotiation_agent, brief_generator, followup_agent


@pytest.fixture(autouse=True)
def clear_sessions():
    """Clear session store between tests."""
    session_store.clear_all()
    yield
    session_store.clear_all()


def _make_stop_response(content="This is a mock negotiation analysis."):
    """Build a mock Responses API response with a text message output."""
    return _build_response("stop", content=content)


def _make_function_call_response(fn_name, fn_args):
    """Build a mock Responses API response with a function_call output."""
    return _build_response("function_call", fn_name=fn_name, fn_args=fn_args)


@pytest.fixture
def mock_openai_single_turn():
    """Mock that returns a stop response on the first call.

    Used for brief generator and follow-up agent tests.
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

    mock_create = MagicMock(side_effect=[
        # First call: negotiation agent (single turn -- no tool calls)
        _build_response("stop", content="Raw analysis: rates are above market median."),
        # Second call: brief generator formatting
        _build_response("stop", content=mock_brief_json),
    ])
    with patch.object(negotiation_agent.client.responses, "create", mock_create), \
         patch.object(brief_generator.client.responses, "create", mock_create):
        yield mock_create


@pytest.fixture
def mock_openai_with_tool_call():
    """Mock that simulates a tool call loop.

    Call sequence:
    1. function_call to get_lease_history
    2. function_call to get_negotiation_notes
    3. function_call to lease_comparables
    4. stop with final analysis
    5. stop for brief generator formatting

    This exercises a realistic 3-tool-call sequence before the final completion.
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

    mock_create = MagicMock(side_effect=[
        # Call 1: agent retrieves internal lease history first
        _build_response("function_call", fn_name="get_lease_history", fn_args={
            "tower_id": "ATT-FL-4205",
        }),
        # Call 2: agent retrieves CRM negotiation notes
        _build_response("function_call", fn_name="get_negotiation_notes", fn_args={
            "provider": "sba_communications",
        }),
        # Call 3: agent pulls market comparables
        _build_response("function_call", fn_name="lease_comparables", fn_args={
            "region": "southeast",
            "tower_type": "ground_mount",
        }),
        # Call 4: agent returns final analysis
        _build_response("stop", content=(
            "Based on internal lease history, CRM intelligence, and comparable analysis, "
            "the current rate of $3200/mo is above the regional median of $2800. "
            "AT&T has strong leverage due to multi-tenant occupancy."
        )),
        # Call 5: brief generator formatting
        _build_response("stop", content=mock_brief_json),
    ])
    with patch.object(negotiation_agent.client.responses, "create", mock_create), \
         patch.object(brief_generator.client.responses, "create", mock_create):
        yield mock_create


@pytest.fixture
def mock_openai_followup():
    """Mock for follow-up agent tests."""
    mock_create = MagicMock(return_value=_build_response(
        "stop",
        content="If they push back on comparables, reference the post-2021 Crown Castle master agreement rates.",
    ))
    with patch.object(followup_agent.client.responses, "create", mock_create):
        yield mock_create


def _build_response(finish_reason, content=None, fn_name=None, fn_args=None):
    """Helper to build a properly structured mock Responses API response object."""
    response = MagicMock()

    if finish_reason == "function_call":
        fc_item = MagicMock()
        fc_item.type = "function_call"
        fc_item.name = fn_name
        fc_item.arguments = json.dumps(fn_args) if fn_args else "{}"
        fc_item.call_id = "call_%s" % fn_name
        response.output = [fc_item]
        response.output_text = None
    else:
        msg_item = MagicMock()
        msg_item.type = "message"
        response.output = [msg_item]
        response.output_text = content or ""

    return response
