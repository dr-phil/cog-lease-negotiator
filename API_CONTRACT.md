# TowerLease Intelligence — API Contract

## Base URL

```
http://localhost:8000
```

---

## Endpoints

### 1. `GET /api/towers`

List all towers in the AT&T inventory.

**Request:** No parameters required.

**Response Schema:**

| Field | Type | Description |
|-------|------|-------------|
| `towers` | `array[TowerInfo]` | List of tower objects |
| `count` | `integer` | Total number of towers |

Each `TowerInfo` object:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tower_id` | `string` | yes | AT&T tower identifier |
| `nickname` | `string` | yes | Human-readable tower name |
| `provider` | `string` | yes | Tower provider identifier |
| `region` | `string` | yes | Geographic region |
| `tower_type` | `string` | yes | Type of tower installation |
| `current_monthly_rate` | `integer` | yes | Current monthly lease rate in USD |
| `lease_expiry` | `string` | yes | Lease expiration date (YYYY-MM-DD) |
| `coordinates` | `object` | yes | `{ "lat": float, "lng": float }` |

**Example `curl`:**

```bash
curl -s http://localhost:8000/api/towers | python -m json.tool
```

**Example Response:**

```json
{
  "towers": [
    {
      "tower_id": "ATT-NY-1201",
      "nickname": "Midtown East Rooftop",
      "provider": "crown_castle",
      "region": "northeast",
      "tower_type": "rooftop",
      "current_monthly_rate": 18500,
      "lease_expiry": "2025-11-01",
      "coordinates": { "lat": 40.7549, "lng": -73.9724 }
    }
  ],
  "count": 15
}
```

**Error Responses:**

| Status Code | Description |
|-------------|-------------|
| `200` | Success |

---

### 2. `POST /api/negotiate`

Generate a negotiation brief for a tower lease renewal. Runs the negotiation agent (multiple tool calls), passes output through the brief generator, and stores a session for follow-up.

**Request Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tower_id` | `string` | yes | AT&T tower identifier |
| `provider` | `string` | yes | Provider: `crown_castle`, `american_tower`, `sba_communications`, `municipal`, `rural_individual` |
| `region` | `string` | yes | Region: `northeast`, `southeast`, `midwest`, `west` |
| `current_monthly_rate` | `integer` | yes | Current monthly lease rate in USD |
| `lease_expiry` | `string` | yes | Lease expiration date (YYYY-MM-DD) |
| `lease_years_remaining` | `float` | yes | Years remaining on current lease |

**Response Schema:**

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | `string` | UUID for follow-up questions |
| `brief` | `string` | 2-3 paragraph executive summary |
| `recommended_opening_rate` | `integer` | Rate AT&T should open negotiations with |
| `walk_away_rate` | `integer` | Maximum rate AT&T should accept |
| `key_leverage_points` | `array[string]` | List of negotiation leverage points |
| `comparable_rates` | `object` | `{ "low": int, "median": int, "high": int }` |
| `provider_context` | `string` | Provider-specific considerations |
| `region_context` | `string` | Regional market conditions |
| `negotiation_history_summary` | `string` | Summary of historical lease negotiations from LeaseTrack; notes if data quality is low/sparse |
| `crm_intelligence` | `string` | Summary of CRM relationship intelligence from NegotiatorCRM; notes if data quality is low/sparse or if sparse_data_warning was flagged |

**Example `curl`:**

```bash
curl -s -X POST http://localhost:8000/api/negotiate \
  -H "Content-Type: application/json" \
  -d '{
    "tower_id": "ATT-FL-4205",
    "provider": "sba_communications",
    "region": "southeast",
    "current_monthly_rate": 3200,
    "lease_expiry": "2025-07-01",
    "lease_years_remaining": 0.5
  }' | python -m json.tool
```

**Example Response:**

```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "brief": "AT&T's current lease rate of $3,200/mo for the Tampa Bay Ground Mount site is approximately 10% above the regional median...",
  "recommended_opening_rate": 2700,
  "walk_away_rate": 3050,
  "key_leverage_points": [
    "Comparable rates show current lease is 15% above median",
    "Tower utilization at 75% -- multi-tenant leverage",
    "Property assessed value supports lower rate"
  ],
  "comparable_rates": {
    "low": 2400,
    "median": 2900,
    "high": 3600
  },
  "provider_context": "SBA Communications is a preferred-tier provider responsive to data-driven arguments.",
  "region_context": "Southeast regional rates trending down for ground mount towers.",
  "negotiation_history_summary": "Historical rates show consistent 4-5% annual escalation. Last negotiated in 2022. Data quality: medium.",
  "crm_intelligence": "SBA Communications is a preferred-tier provider. Account team restructured in Q4 2023. New regional director is more data-driven."
}
```

**Error Responses:**

| Status Code | Description |
|-------------|-------------|
| `200` | Success |
| `422` | Validation error — missing or invalid request fields |

---

### 3. `POST /api/followup`

Ask a follow-up question about a previously generated negotiation brief.

**Request Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | `string` | yes | Session UUID from `/api/negotiate` response |
| `question` | `string` | yes | Follow-up question text |

**Response Schema:**

| Field | Type | Description |
|-------|------|-------------|
| `answer` | `string` | The agent's answer to the follow-up question |
| `session_id` | `string` | Echo of the session ID |

**Example `curl`:**

```bash
curl -s -X POST http://localhost:8000/api/followup \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "question": "What if they push back on the comparable data?"
  }' | python -m json.tool
```

**Example Response:**

```json
{
  "answer": "If they push back on comparables, reference the post-2021 Crown Castle master agreement rates which set a regional benchmark.",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Error Responses:**

| Status Code | Description |
|-------------|-------------|
| `200` | Success |
| `404` | Session expired or not found — client should prompt user to regenerate via `/api/negotiate` |
| `422` | Validation error — missing or invalid request fields |

---

## Session Lifecycle

- Sessions are stored **in-memory** and do **not survive server restarts**.
- Each call to `POST /api/negotiate` creates a new session and returns a `session_id`.
- Follow-up questions via `POST /api/followup` require a valid `session_id`.
- Clients should handle `404` on `/api/followup` by prompting the user to regenerate a new brief via `/api/negotiate`.
- No authentication is currently implemented.

---

## Tower Inventory

The following 15 towers are returned by `GET /api/towers`:

| Tower ID | Nickname | Provider | Region | Tower Type |
|----------|----------|----------|--------|------------|
| ATT-NY-1201 | Midtown East Rooftop | crown_castle | northeast | rooftop |
| ATT-GA-3302 | Peachtree Industrial | crown_castle | southeast | monopole |
| ATT-CA-7701 | Bay Area Ground Site | crown_castle | west | ground_mount |
| ATT-MA-1502 | Boston Harbor Rooftop | american_tower | northeast | rooftop |
| ATT-FL-4101 | Orlando East Monopole | american_tower | southeast | monopole |
| ATT-IL-5501 | Chicago West Loop | american_tower | midwest | rooftop |
| ATT-FL-4205 | Tampa Bay Ground Mount | sba_communications | southeast | ground_mount |
| ATT-OH-6001 | Columbus Westside | sba_communications | midwest | monopole |
| ATT-AZ-8101 | Phoenix North Monopole | sba_communications | west | monopole |
| ATT-IN-5801 | Carmel Water Tower | municipal | midwest | water_tower |
| ATT-NC-3501 | Durham Municipal Tower | municipal | southeast | water_tower |
| ATT-CT-1301 | Hartford City Rooftop | municipal | northeast | rooftop |
| ATT-IA-5901 | Cedar Rapids Farm Site | rural_individual | midwest | ground_mount |
| ATT-MT-8501 | Billings Ranch Ground | rural_individual | west | ground_mount |
| ATT-AL-3701 | Huntsville Rural Site | rural_individual | southeast | ground_mount |

---

## Known Limitations

- **In-memory session store**: Sessions are stored in a Python dict and do not persist across server restarts. All active sessions are lost on restart.
- **No authentication implemented**: All endpoints are open. The service is intended to run behind AT&T's internal VPN.
- **Internal service responses are deterministic-but-fake (mocked)**: The tools (property lookup, lease comparables, tower utilization, regulatory lookup, lease history, and negotiation notes) return realistic mock data seeded by input parameters. They do not connect to real internal APIs.
- **TODO**: Move sessions to Redis before multi-region rollout (see JIRA-2201).
