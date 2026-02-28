"""
Pydantic v1 request/response models for the TowerLease Intelligence API.

Using Pydantic v1 style throughout -- no model_ prefix methods.
This predates the Pydantic v2 migration that the platform team keeps
threatening to do but never actually schedules.
"""
from typing import List, Dict, Optional
from pydantic import BaseModel


class NegotiateRequest(BaseModel):
    tower_id: str
    provider: str
    region: str
    current_monthly_rate: int
    lease_expiry: str
    lease_years_remaining: float


class ComparableRates(BaseModel):
    low: int
    median: int
    high: int


class NegotiateResponse(BaseModel):
    session_id: str
    brief: str
    recommended_opening_rate: int
    walk_away_rate: int
    key_leverage_points: List[str]
    comparable_rates: ComparableRates
    provider_context: str
    region_context: str
    negotiation_history_summary: str
    crm_intelligence: str


class FollowupRequest(BaseModel):
    session_id: str
    question: str


class FollowupResponse(BaseModel):
    answer: str
    session_id: str


class TowerInfo(BaseModel):
    tower_id: str
    nickname: str
    provider: str
    region: str
    tower_type: str
    current_monthly_rate: int
    lease_expiry: str
    coordinates: Dict[str, float]


class TowerListResponse(BaseModel):
    towers: List[TowerInfo]
    count: int
