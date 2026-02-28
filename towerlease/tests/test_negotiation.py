"""
Tests for the negotiation agent, brief generator, and follow-up agent.

Covers:
  - One flow per provider type
  - Tool call dispatch loop
  - Brief generation
  - Follow-up Q&A continuity
"""
import json
import pytest
from unittest.mock import patch

from towerlease.agents.negotiation_agent import (
    run_negotiation_agent,
    dispatch_tool,
    build_system_prompt,
    build_initial_message,
)
from towerlease.agents.brief_generator import generate_brief
from towerlease.agents.followup_agent import handle_followup
from towerlease.server import session_store


# -- Tool dispatch tests --

class TestToolDispatch:
    def test_property_lookup_dispatch(self):
        result = dispatch_tool("property_lookup", {"tower_id": "ATT-TX-4821"})
        assert "owner_name" in result
        assert "parcel_id" in result
        assert result["tower_id"] == "ATT-TX-4821"

    def test_lease_comparables_dispatch(self):
        result = dispatch_tool("lease_comparables", {
            "region": "southeast",
            "tower_type": "ground_mount",
        })
        assert isinstance(result, list)
        assert len(result) == 5
        assert "monthly_rate" in result[0]

    def test_tower_utilization_dispatch(self):
        result = dispatch_tool("tower_utilization", {"tower_id": "ATT-GA-3302"})
        assert "tenants" in result
        assert result["tower_id"] == "ATT-GA-3302"
        # AT&T should always be a tenant
        carriers = [t["carrier"] for t in result["tenants"]]
        assert "AT&T" in carriers

    def test_regulatory_lookup_dispatch(self):
        result = dispatch_tool("regulatory_lookup", {
            "region": "west",
            "tower_type": "monopole",
        })
        assert "relevant_statutes" in result
        assert "regulatory_risk_level" in result

    def test_unknown_tool_returns_error(self):
        result = dispatch_tool("nonexistent_tool", {})
        assert "error" in result

    def test_bad_args_returns_error(self):
        result = dispatch_tool("property_lookup", {"bad_arg": "value"})
        assert "error" in result


# -- System prompt and message building tests --

class TestPromptBuilding:
    def test_build_system_prompt_crown_castle(self):
        prompt = build_system_prompt("crown_castle", "northeast")
        assert "Crown Castle" in prompt
        assert "2,400" in prompt
        assert "REGION MARKET CONTEXT" in prompt

    def test_build_system_prompt_municipal(self):
        prompt = build_system_prompt("municipal", "midwest")
        assert "municipal" in prompt.lower()
        assert "council" in prompt.lower()

    def test_build_system_prompt_rural(self):
        prompt = build_system_prompt("rural_individual", "west")
        assert "individual" in prompt.lower() or "landowner" in prompt.lower()

    def test_build_initial_message(self):
        lease_data = {
            "tower_id": "ATT-FL-4205",
            "current_monthly_rate": 3200,
            "lease_expiry": "2025-07-01",
            "lease_years_remaining": 0.5,
        }
        msg = build_initial_message("ATT-FL-4205", lease_data, "sba_communications", "southeast")
        assert "ATT-FL-4205" in msg
        assert "3200" in msg


# -- Agent loop tests with mocked OpenAI --

class TestNegotiationAgent:
    def test_single_turn_flow(self, mock_openai_single_turn):
        """Test agent with no tool calls -- direct stop response."""
        result, messages = run_negotiation_agent(
            tower_id="ATT-FL-4205",
            lease_data={
                "tower_id": "ATT-FL-4205",
                "current_monthly_rate": 3200,
                "lease_expiry": "2025-07-01",
                "lease_years_remaining": 0.5,
            },
            provider="sba_communications",
            region="southeast",
        )
        assert result is not None
        assert len(messages) >= 3  # system + user + assistant

    def test_tool_call_flow(self, mock_openai_with_tool_call):
        """Test the full agent loop with tool calls."""
        result, messages = run_negotiation_agent(
            tower_id="ATT-FL-4205",
            lease_data={
                "tower_id": "ATT-FL-4205",
                "current_monthly_rate": 3200,
                "lease_expiry": "2025-07-01",
                "lease_years_remaining": 0.5,
            },
            provider="sba_communications",
            region="southeast",
        )
        assert result is not None
        assert "above" in result.lower() or "median" in result.lower()

        # Should have system + user + (fn_call + fn_result) * 3 + final assistant
        assert len(messages) >= 8

        # Verify tool call messages are in the history
        fn_messages = [m for m in messages if m.get("role") == "function"]
        assert len(fn_messages) == 3


class TestNegotiationPerProvider:
    """One flow per provider type to ensure prompt building works for all."""

    @pytest.fixture(autouse=True)
    def _setup_mock(self):
        """Set up a simple single-turn mock for all provider tests."""
        with patch("openai.ChatCompletion.create") as mock:
            mock.return_value = {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "Analysis complete for this provider.",
                    },
                    "finish_reason": "stop",
                }]
            }
            self.mock_create = mock
            yield

    def _run_for_provider(self, provider, region):
        return run_negotiation_agent(
            tower_id="ATT-TEST-0001",
            lease_data={
                "tower_id": "ATT-TEST-0001",
                "current_monthly_rate": 3000,
                "lease_expiry": "2025-08-01",
                "lease_years_remaining": 0.5,
            },
            provider=provider,
            region=region,
        )

    def test_crown_castle(self):
        result, _ = self._run_for_provider("crown_castle", "northeast")
        assert result is not None

    def test_american_tower(self):
        result, _ = self._run_for_provider("american_tower", "southeast")
        assert result is not None

    def test_sba_communications(self):
        result, _ = self._run_for_provider("sba_communications", "midwest")
        assert result is not None

    def test_municipal(self):
        result, _ = self._run_for_provider("municipal", "southeast")
        assert result is not None

    def test_rural_individual(self):
        result, _ = self._run_for_provider("rural_individual", "west")
        assert result is not None


# -- Brief generator tests --

class TestBriefGenerator:
    def test_generate_brief(self, mock_openai_single_turn):
        """Test that brief generator produces structured output."""
        raw = "The current rate of $3200 is above the regional median."
        tower_data = {"current_monthly_rate": 3200}
        # The mock_openai_single_turn has two responses queued;
        # we need to consume the first one (negotiation agent) before
        # the brief generator call. So we use a fresh mock here.
        with patch("openai.ChatCompletion.create") as mock_create:
            mock_create.return_value = {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": json.dumps({
                            "brief": "Test brief",
                            "recommended_opening_rate": 2800,
                            "walk_away_rate": 3100,
                            "key_leverage_points": ["point1"],
                            "comparable_rates": {"low": 2600, "median": 3000, "high": 3800},
                            "provider_context": "ctx",
                            "region_context": "rctx",
                        }),
                    },
                    "finish_reason": "stop",
                }]
            }
            brief = generate_brief(raw, tower_data)

        assert "brief" in brief
        assert "recommended_opening_rate" in brief
        assert "walk_away_rate" in brief
        assert "key_leverage_points" in brief
        assert "comparable_rates" in brief

    def test_brief_fallback_on_bad_json(self):
        """Test that brief generator handles malformed JSON gracefully."""
        with patch("openai.ChatCompletion.create") as mock_create:
            mock_create.return_value = {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "This is not JSON at all",
                    },
                    "finish_reason": "stop",
                }]
            }
            brief = generate_brief("raw analysis text", {"current_monthly_rate": 3000})

        # Should fall back to default structure
        assert "brief" in brief
        assert isinstance(brief["recommended_opening_rate"], int)


# -- Follow-up agent tests --

class TestFollowupAgent:
    def test_followup_basic(self, mock_openai_followup):
        """Test basic follow-up question."""
        messages = [
            {"role": "system", "content": "You are a negotiation agent."},
            {"role": "user", "content": "Prepare a brief."},
            {"role": "assistant", "content": "Here is the brief."},
        ]

        answer, updated = handle_followup(messages, "What about comparables?")
        assert answer is not None
        assert len(updated) > len(messages)
        # Should have added user question and assistant response
        assert updated[-2]["role"] == "user"
        assert updated[-1]["role"] == "assistant"

    def test_followup_preserves_history(self, mock_openai_followup):
        """Test that follow-up doesn't mutate the original messages."""
        original_messages = [
            {"role": "system", "content": "You are a negotiation agent."},
            {"role": "user", "content": "Prepare a brief."},
            {"role": "assistant", "content": "Here is the brief."},
        ]
        original_len = len(original_messages)

        answer, updated = handle_followup(original_messages, "Follow-up question")
        # Original should not be mutated
        assert len(original_messages) == original_len

    def test_followup_with_session_store(self, mock_openai_followup):
        """Test follow-up through the session store flow."""
        messages = [
            {"role": "system", "content": "System prompt here."},
            {"role": "assistant", "content": "Initial brief."},
        ]
        session_id = session_store.create_session(messages)

        stored = session_store.get_messages(session_id)
        assert stored is not None

        answer, updated = handle_followup(stored, "Test question")
        session_store.update_session(session_id, updated)

        # Verify updated messages are stored
        final = session_store.get_messages(session_id)
        assert len(final) > len(messages)
