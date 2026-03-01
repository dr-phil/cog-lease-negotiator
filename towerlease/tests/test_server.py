"""
Tests for the FastAPI server endpoints.

Uses FastAPI's TestClient (httpx-based) to test:
  - GET /api/towers returns 15 towers with correct schema
  - POST /api/negotiate returns correct response shape
  - POST /api/followup with valid session returns answer
  - POST /api/followup with invalid session returns 404
"""
import json
import pytest
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from towerlease.server.main import app
from towerlease.server import session_store
from towerlease.server.schemas import NegotiateResponse
from towerlease.agents import negotiation_agent, brief_generator, followup_agent
from towerlease.tests.conftest import _build_response


client = TestClient(app)


class TestTowersEndpoint:
    def test_list_towers_returns_15(self):
        response = client.get("/api/towers")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 15
        assert len(data["towers"]) == 15

    def test_tower_schema(self):
        response = client.get("/api/towers")
        data = response.json()
        tower = data["towers"][0]

        # Verify all required fields
        required_fields = [
            "tower_id", "nickname", "provider", "region",
            "tower_type", "current_monthly_rate", "lease_expiry",
            "coordinates",
        ]
        for field in required_fields:
            assert field in tower, "Missing field: %s" % field

        # Verify coordinates have lat/lng
        assert "lat" in tower["coordinates"]
        assert "lng" in tower["coordinates"]

    def test_towers_have_all_providers(self):
        response = client.get("/api/towers")
        data = response.json()
        providers = set(t["provider"] for t in data["towers"])
        expected = {"crown_castle", "american_tower", "sba_communications", "municipal", "rural_individual"}
        assert providers == expected

    def test_towers_have_all_regions(self):
        response = client.get("/api/towers")
        data = response.json()
        regions = set(t["region"] for t in data["towers"])
        expected = {"northeast", "southeast", "midwest", "west"}
        assert regions == expected

    def test_towers_have_all_types(self):
        """Verify at least rooftop, ground_mount, monopole, and water_tower appear."""
        response = client.get("/api/towers")
        data = response.json()
        types = set(t["tower_type"] for t in data["towers"])
        expected = {"rooftop", "ground_mount", "monopole", "water_tower"}
        assert expected.issubset(types)


class TestNegotiateEndpoint:
    def test_negotiate_returns_correct_shape(self):
        """Test POST /api/negotiate returns the expected response structure."""
        mock_brief_json = json.dumps({
            "brief": "Test negotiation brief.",
            "recommended_opening_rate": 2800,
            "walk_away_rate": 3100,
            "key_leverage_points": ["Leverage point 1", "Leverage point 2"],
            "comparable_rates": {"low": 2600, "median": 3000, "high": 3800},
            "provider_context": "Provider context here.",
            "region_context": "Region context here.",
            "negotiation_history_summary": "Historical rates show 4% annual escalation.",
            "crm_intelligence": "Provider has strategic relationship tier with AT&T.",
        })

        mock_create = MagicMock(side_effect=[
            # Negotiation agent: stop immediately
            _build_response("stop", content="Raw analysis."),
            # Brief generator
            _build_response("stop", content=mock_brief_json),
        ])
        with patch.object(negotiation_agent.client.responses, "create", mock_create), \
             patch.object(brief_generator.client.responses, "create", mock_create):

            response = client.post("/api/negotiate", json={
                "tower_id": "ATT-FL-4205",
                "provider": "sba_communications",
                "region": "southeast",
                "current_monthly_rate": 3200,
                "lease_expiry": "2025-07-01",
                "lease_years_remaining": 0.5,
            })

        assert response.status_code == 200
        data = response.json()

        # Check all required fields
        assert "session_id" in data
        assert "brief" in data
        assert "recommended_opening_rate" in data
        assert "walk_away_rate" in data
        assert "key_leverage_points" in data
        assert "comparable_rates" in data
        assert "provider_context" in data
        assert "region_context" in data
        assert "negotiation_history_summary" in data
        assert "crm_intelligence" in data

        # Verify types
        assert isinstance(data["session_id"], str)
        assert isinstance(data["recommended_opening_rate"], int)
        assert isinstance(data["key_leverage_points"], list)
        assert isinstance(data["comparable_rates"], dict)


class TestFollowupEndpoint:
    def test_followup_with_valid_session(self):
        """Test POST /api/followup with a valid session ID."""
        # First, create a session manually
        messages = [
            {"role": "system", "content": "Test system prompt."},
            {"role": "user", "content": "Test user message."},
            {"role": "assistant", "content": "Test assistant response."},
        ]
        session_id = session_store.create_session(messages)

        mock_create = MagicMock(return_value=_build_response(
            "stop", content="Here is the follow-up answer.",
        ))
        with patch.object(followup_agent.client.responses, "create", mock_create):

            response = client.post("/api/followup", json={
                "session_id": session_id,
                "question": "What about the comparable data?",
            })

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert data["session_id"] == session_id
        assert data["answer"] == "Here is the follow-up answer."

    def test_followup_with_invalid_session_returns_404(self):
        """Test POST /api/followup with a nonexistent session ID."""
        response = client.post("/api/followup", json={
            "session_id": "nonexistent-session-id-12345",
            "question": "This should fail.",
        })

        assert response.status_code == 404
        data = response.json()
        assert "Session expired or not found" in data["detail"]

    def test_followup_updates_session(self):
        """Test that follow-up correctly updates the session store."""
        messages = [
            {"role": "system", "content": "System."},
            {"role": "assistant", "content": "Brief."},
        ]
        session_id = session_store.create_session(messages)

        mock_create = MagicMock(return_value=_build_response(
            "stop", content="Answer 1.",
        ))
        with patch.object(followup_agent.client.responses, "create", mock_create):

            client.post("/api/followup", json={
                "session_id": session_id,
                "question": "Question 1",
            })

        # Session should now have more messages
        updated = session_store.get_messages(session_id)
        assert len(updated) > len(messages)


class TestNegotiateResponseSchema:
    """Verify that NegotiateResponse includes the new fields."""

    def test_negotiate_response_has_negotiation_history_summary(self):
        """Test that NegotiateResponse includes negotiation_history_summary field."""
        fields = NegotiateResponse.__fields__
        assert "negotiation_history_summary" in fields
        assert fields["negotiation_history_summary"].outer_type_ is str

    def test_negotiate_response_has_crm_intelligence(self):
        """Test that NegotiateResponse includes crm_intelligence field."""
        fields = NegotiateResponse.__fields__
        assert "crm_intelligence" in fields
        assert fields["crm_intelligence"].outer_type_ is str

    def test_negotiate_response_full_shape(self):
        """Test that NegotiateResponse has all expected fields."""
        expected_fields = {
            "session_id", "brief", "recommended_opening_rate", "walk_away_rate",
            "key_leverage_points", "comparable_rates", "provider_context",
            "region_context", "negotiation_history_summary", "crm_intelligence",
        }
        actual_fields = set(NegotiateResponse.__fields__.keys())
        assert expected_fields == actual_fields


class TestHealthCheck:
    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
