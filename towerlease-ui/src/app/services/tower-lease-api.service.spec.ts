import { TestBed } from '@angular/core/testing';
import {
  HttpClientTestingModule,
  HttpTestingController,
} from '@angular/common/http/testing';
import { TowerLeaseApiService } from './tower-lease-api.service';
import { environment } from '../../environments/environment';
import {
  TowerInfo,
  NegotiateRequest,
  NegotiateResponse,
  FollowupRequest,
  FollowupResponse,
} from '../models/tower-lease.models';

describe('TowerLeaseApiService', () => {
  let service: TowerLeaseApiService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [TowerLeaseApiService],
    });
    service = TestBed.inject(TowerLeaseApiService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  describe('getTowers()', () => {
    it('should call GET /api/towers and deserialize into TowerInfo[] with all required fields', () => {
      const mockTower: TowerInfo = {
        tower_id: 'ATT-FL-4205',
        nickname: 'Tampa Bay Ground Mount',
        provider: 'sba_communications',
        region: 'southeast',
        tower_type: 'ground_mount',
        current_monthly_rate: 3200,
        lease_expiry: '2025-07-01',
        coordinates: { lat: 27.9506, lng: -82.4572 },
      };

      const mockResponse = { towers: [mockTower], count: 1 };

      service.getTowers().subscribe((res) => {
        expect(res.towers.length).toBe(1);
        expect(res.count).toBe(1);

        const tower = res.towers[0];
        // Verify all required fields matching backend schema (test_server.py lines 38-48)
        expect(tower.tower_id).toBe('ATT-FL-4205');
        expect(tower.nickname).toBe('Tampa Bay Ground Mount');
        expect(tower.provider).toBe('sba_communications');
        expect(tower.region).toBe('southeast');
        expect(tower.tower_type).toBe('ground_mount');
        expect(tower.current_monthly_rate).toBe(3200);
        expect(tower.lease_expiry).toBe('2025-07-01');
        expect(tower.coordinates).toBeDefined();
        expect(tower.coordinates.lat).toBe(27.9506);
        expect(tower.coordinates.lng).toBe(-82.4572);
      });

      const req = httpMock.expectOne(`${environment.apiBase}/api/towers`);
      expect(req.request.method).toBe('GET');
      req.flush(mockResponse);
    });

    it('should deserialize multiple towers preserving all fields', () => {
      const mockTowers: TowerInfo[] = [
        {
          tower_id: 'ATT-NY-1201',
          nickname: 'Midtown East Rooftop',
          provider: 'crown_castle',
          region: 'northeast',
          tower_type: 'rooftop',
          current_monthly_rate: 18500,
          lease_expiry: '2025-11-01',
          coordinates: { lat: 40.7549, lng: -73.9724 },
        },
        {
          tower_id: 'ATT-FL-4205',
          nickname: 'Tampa Bay Ground Mount',
          provider: 'sba_communications',
          region: 'southeast',
          tower_type: 'ground_mount',
          current_monthly_rate: 3200,
          lease_expiry: '2025-07-01',
          coordinates: { lat: 27.9506, lng: -82.4572 },
        },
      ];

      service.getTowers().subscribe((res) => {
        expect(res.towers.length).toBe(2);
        expect(res.count).toBe(2);
        // Ensure each tower has coordinates with lat and lng
        res.towers.forEach((tower) => {
          expect(tower.coordinates).toBeDefined();
          expect(typeof tower.coordinates.lat).toBe('number');
          expect(typeof tower.coordinates.lng).toBe('number');
        });
      });

      const req = httpMock.expectOne(`${environment.apiBase}/api/towers`);
      req.flush({ towers: mockTowers, count: 2 });
    });
  });

  describe('negotiate()', () => {
    it('should send a POST with all required NegotiateRequest fields', () => {
      const request: NegotiateRequest = {
        tower_id: 'ATT-FL-4205',
        provider: 'sba_communications',
        region: 'southeast',
        current_monthly_rate: 3200,
        lease_expiry: '2025-07-01',
        lease_years_remaining: 0.5,
      };

      const mockResponse: NegotiateResponse = {
        session_id: 'test-session-id-123',
        brief: 'Test negotiation brief.',
        recommended_opening_rate: 2800,
        walk_away_rate: 3100,
        key_leverage_points: ['Leverage point 1', 'Leverage point 2'],
        comparable_rates: { low: 2600, median: 3000, high: 3800 },
        provider_context: 'Provider context here.',
        region_context: 'Region context here.',
        negotiation_history_summary: 'Historical rates show 4% annual escalation.',
        crm_intelligence: 'Provider has strategic relationship tier with AT&T.',
      };

      service.negotiate(request).subscribe((res) => {
        expect(res).toBeTruthy();
      });

      const req = httpMock.expectOne(`${environment.apiBase}/api/negotiate`);
      expect(req.request.method).toBe('POST');

      // Verify outgoing payload has all required NegotiateRequest fields
      const body = req.request.body as NegotiateRequest;
      expect(body.tower_id).toBe('ATT-FL-4205');
      expect(body.provider).toBe('sba_communications');
      expect(body.region).toBe('southeast');
      expect(body.current_monthly_rate).toBe(3200);
      expect(body.lease_expiry).toBe('2025-07-01');
      expect(body.lease_years_remaining).toBe(0.5);

      req.flush(mockResponse);
    });

    it('should correctly deserialize a NegotiateResponse with all fields', () => {
      const request: NegotiateRequest = {
        tower_id: 'ATT-FL-4205',
        provider: 'sba_communications',
        region: 'southeast',
        current_monthly_rate: 3200,
        lease_expiry: '2025-07-01',
        lease_years_remaining: 0.5,
      };

      const mockResponse: NegotiateResponse = {
        session_id: 'test-session-id-456',
        brief: 'Test negotiation brief.',
        recommended_opening_rate: 2800,
        walk_away_rate: 3100,
        key_leverage_points: ['Leverage point 1', 'Leverage point 2'],
        comparable_rates: { low: 2600, median: 3000, high: 3800 },
        provider_context: 'Provider context here.',
        region_context: 'Region context here.',
        negotiation_history_summary: 'Historical rates show 4% annual escalation.',
        crm_intelligence: 'Provider has strategic relationship tier with AT&T.',
      };

      service.negotiate(request).subscribe((res) => {
        // Verify all NegotiateResponse fields (matching test_server.py lines 118-134)
        expect(res.session_id).toBe('test-session-id-456');
        expect(res.brief).toBe('Test negotiation brief.');
        expect(res.recommended_opening_rate).toBe(2800);
        expect(res.walk_away_rate).toBe(3100);
        expect(res.key_leverage_points).toEqual(['Leverage point 1', 'Leverage point 2']);
        expect(res.comparable_rates).toEqual({ low: 2600, median: 3000, high: 3800 });
        expect(res.provider_context).toBe('Provider context here.');
        expect(res.region_context).toBe('Region context here.');
        expect(res.negotiation_history_summary).toBe('Historical rates show 4% annual escalation.');
        expect(res.crm_intelligence).toBe('Provider has strategic relationship tier with AT&T.');
      });

      const req = httpMock.expectOne(`${environment.apiBase}/api/negotiate`);
      req.flush(mockResponse);
    });
  });

  describe('followup()', () => {
    it('should send a POST with session_id and question, and parse FollowupResponse', () => {
      const request: FollowupRequest = {
        session_id: 'test-session-id-789',
        question: 'What about the comparable data?',
      };

      const mockResponse: FollowupResponse = {
        answer: 'Here is the follow-up answer.',
        session_id: 'test-session-id-789',
      };

      service.followup(request).subscribe((res) => {
        // Verify FollowupResponse fields (matching test_server.py lines 164-168)
        expect(res.answer).toBe('Here is the follow-up answer.');
        expect(res.session_id).toBe('test-session-id-789');
      });

      const req = httpMock.expectOne(`${environment.apiBase}/api/followup`);
      expect(req.request.method).toBe('POST');

      // Verify outgoing payload has session_id and question
      const body = req.request.body as FollowupRequest;
      expect(body.session_id).toBe('test-session-id-789');
      expect(body.question).toBe('What about the comparable data?');

      req.flush(mockResponse);
    });

    it('should propagate an HTTP 404 error as an observable error when session_id is stale', () => {
      const request: FollowupRequest = {
        session_id: 'nonexistent-session-id-12345',
        question: 'This should fail.',
      };

      service.followup(request).subscribe({
        next: () => fail('Expected an error, not a success'),
        error: (err) => {
          // Matching backend behavior: test_server.py lines 170-179
          expect(err.status).toBe(404);
        },
      });

      const req = httpMock.expectOne(`${environment.apiBase}/api/followup`);
      req.flush(
        { detail: 'Session expired or not found' },
        { status: 404, statusText: 'Not Found' }
      );
    });
  });
});
