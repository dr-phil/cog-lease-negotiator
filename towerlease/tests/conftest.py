"""
Test fixtures for TowerLease Intelligence.

Mocks openai.ChatCompletion.create to avoid hitting the real API in tests.
Two fixtures:
  - mock_openai_single_turn: returns a stop response directly
  - mock_openai_with_tool_call: simulates a tool call loop (function_call then stop)
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


def _make_stop_response(content="This is a mock negotiation analysis."):
    """Build a mock ChatCompletion response with finish_reason: stop."""
    response = MagicMock()
    message = {
        "role": "assistant",
        "content": content,
    }
    response.__getitem__ = lambda self, key: {
        "choices": [{"message": message, "finish_reason": "stop"}],
    }[key]
    return response


def _make_function_call_response(fn_name, fn_args):
    """Build a mock ChatCompletion response with finish_reason: function_call."""
    response = MagicMock()
    message = {
        "role": "assistant",
        "content": None,
        "function_call": {
            "name": fn_name,
            "arguments": json.dumps(fn_args),
        },
    }
    response.__getitem__ = lambda self, key: {
        "choices": [{"message": message, "finish_reason": "function_call"}],
    }[key]
    return response


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

    with patch("openai.ChatCompletion.create") as mock_create:
        # First call: negotiation agent (single turn -- no tool calls)
        # Second call: brief generator formatting
        mock_create.side_effect = [
            _build_response("stop", content="Raw analysis: rates are above market median."),
            _build_response("stop", content=mock_brief_json),
        ]
        yield mock_create


@pytest.fixture
def mock_openai_with_tool_call():
    """Mock that simulates a tool call loop.

    Call sequence:
    1. function_call to lease_comparables
    2. function_call to property_lookup
    3. function_call to tower_utilization
    4. stop with final analysis
    5. stop for brief generator formatting

    This exercises the full agent loop including tool dispatch.
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
    })

    with patch("openai.ChatCompletion.create") as mock_create:
        mock_create.side_effect = [
            # Call 1: agent wants to look up lease comparables
            _build_response("function_call", fn_name="lease_comparables", fn_args={
                "region": "southeast",
                "tower_type": "ground_mount",
            }),
            # Call 2: agent wants property lookup
            _build_response("function_call", fn_name="property_lookup", fn_args={
                "tower_id": "ATT-FL-4205",
            }),
            # Call 3: agent wants tower utilization
            _build_response("function_call", fn_name="tower_utilization", fn_args={
                "tower_id": "ATT-FL-4205",
            }),
            # Call 4: agent returns final analysis
            _build_response("stop", content=(
                "Based on comparable analysis, property records, and utilization data, "
                "the current rate of $3200/mo is above the regional median of $2800. "
                "AT&T has strong leverage due to multi-tenant occupancy."
            )),
            # Call 5: brief generator formatting
            _build_response("stop", content=mock_brief_json),
        ]
        yield mock_create


@pytest.fixture
def mock_openai_followup():
    """Mock for follow-up agent tests."""
    with patch("openai.ChatCompletion.create") as mock_create:
        mock_create.return_value = _build_response(
            "stop",
            content="If they push back on comparables, reference the post-2021 Crown Castle master agreement rates.",
        )
        yield mock_create


def _build_response(finish_reason, content=None, fn_name=None, fn_args=None):
    """Helper to build a properly structured mock response dict."""
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
