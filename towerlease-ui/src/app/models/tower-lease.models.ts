export interface TowerInfo {
  tower_id: string;
  nickname: string;
  provider: string;
  region: string;
  tower_type: string;
  current_monthly_rate: number;
  lease_expiry: string;
  coordinates: { lat: number; lng: number };
}

export interface NegotiateRequest {
  tower_id: string;
  provider: string;
  region: string;
  current_monthly_rate: number;
  lease_expiry: string;
  lease_years_remaining: number;
}

export interface ComparableRates {
  low: number;
  median: number;
  high: number;
}

export interface NegotiateResponse {
  session_id: string;
  brief: string;
  recommended_opening_rate: number;
  walk_away_rate: number;
  key_leverage_points: string[];
  comparable_rates: ComparableRates;
  provider_context: string;
  region_context: string;
  negotiation_history_summary: string;
  crm_intelligence: string;
}

export interface FollowupRequest {
  session_id: string;
  question: string;
}

export interface FollowupResponse {
  answer: string;
  session_id: string;
}
