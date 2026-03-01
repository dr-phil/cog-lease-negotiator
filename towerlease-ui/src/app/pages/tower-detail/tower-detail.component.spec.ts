import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { of, throwError } from 'rxjs';

import { TowerDetailComponent } from './tower-detail.component';
import { TowerLeaseApiService } from '../../services/tower-lease-api.service';
import {
  TowerInfo,
  NegotiateRequest,
  NegotiateResponse,
} from '../../models/tower-lease.models';

describe('TowerDetailComponent', () => {
  let component: TowerDetailComponent;
  let fixture: ComponentFixture<TowerDetailComponent>;
  let apiSpy: jasmine.SpyObj<TowerLeaseApiService>;
  let router: Router;

  const mockTower: TowerInfo = {
    tower_id: 'ATT-FL-4205',
    nickname: 'Tampa Bay Ground Mount',
    provider: 'sba_communications',
    region: 'southeast',
    tower_type: 'ground_mount',
    current_monthly_rate: 3200,
    lease_expiry: '2027-07-01',
    coordinates: { lat: 27.9506, lng: -82.4572 },
  };

  const mockNegotiateResponse: NegotiateResponse = {
    session_id: 'test-session-id-abc',
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

  function configureTestBed(towerId: string | null): void {
    apiSpy = jasmine.createSpyObj('TowerLeaseApiService', [
      'getTowers',
      'negotiate',
      'followup',
    ]);

    TestBed.configureTestingModule({
      imports: [RouterTestingModule, FormsModule],
      declarations: [TowerDetailComponent],
      providers: [
        { provide: TowerLeaseApiService, useValue: apiSpy },
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              paramMap: {
                get: (key: string) => (key === 'id' ? towerId : null),
              },
            },
          },
        },
      ],
    }).compileComponents();

    router = TestBed.inject(Router);
    spyOn(router, 'navigate');
  }

  describe('on load', () => {
    it('should read tower_id from route params and call getTowers()', () => {
      configureTestBed('ATT-FL-4205');
      apiSpy.getTowers.and.returnValue(
        of({ towers: [mockTower], count: 1 })
      );

      fixture = TestBed.createComponent(TowerDetailComponent);
      component = fixture.componentInstance;
      fixture.detectChanges();

      expect(apiSpy.getTowers).toHaveBeenCalled();
      expect(component.tower).toEqual(mockTower);
      expect(component.currentMonthlyRate).toBe(3200);
      expect(component.leaseExpiry).toBe('2027-07-01');
      expect(component.loading).toBeFalse();
    });

    it('should set error when tower_id is not found in the response', () => {
      configureTestBed('NONEXISTENT-TOWER');
      apiSpy.getTowers.and.returnValue(
        of({ towers: [mockTower], count: 1 })
      );

      fixture = TestBed.createComponent(TowerDetailComponent);
      component = fixture.componentInstance;
      fixture.detectChanges();

      expect(component.tower).toBeNull();
      expect(component.error).toContain('not found');
    });

    it('should set error when no tower_id is provided in route params', () => {
      configureTestBed(null);
      fixture = TestBed.createComponent(TowerDetailComponent);
      component = fixture.componentInstance;
      fixture.detectChanges();

      expect(component.error).toBe('No tower ID provided.');
      expect(apiSpy.getTowers).not.toHaveBeenCalled();
    });
  });

  describe('onSubmit() - negotiate', () => {
    beforeEach(() => {
      configureTestBed('ATT-FL-4205');
      apiSpy.getTowers.and.returnValue(
        of({ towers: [mockTower], count: 1 })
      );

      fixture = TestBed.createComponent(TowerDetailComponent);
      component = fixture.componentInstance;
      fixture.detectChanges();
    });

    it('should call negotiate() with all required NegotiateRequest fields', () => {
      apiSpy.negotiate.and.returnValue(of(mockNegotiateResponse));

      component.onSubmit();

      expect(apiSpy.negotiate).toHaveBeenCalledTimes(1);
      const sentRequest: NegotiateRequest =
        apiSpy.negotiate.calls.mostRecent().args[0];

      // Verify all NegotiateRequest fields
      expect(sentRequest.tower_id).toBe('ATT-FL-4205');
      expect(sentRequest.provider).toBe('sba_communications');
      expect(sentRequest.region).toBe('southeast');
      expect(sentRequest.current_monthly_rate).toBe(3200);
      expect(sentRequest.lease_expiry).toBe('2027-07-01');
      expect(typeof sentRequest.lease_years_remaining).toBe('number');
    });

    it('should store session_id in localStorage and navigate to /brief/:session_id on success', () => {
      apiSpy.negotiate.and.returnValue(of(mockNegotiateResponse));
      spyOn(localStorage, 'setItem');

      component.onSubmit();

      expect(localStorage.setItem).toHaveBeenCalledWith(
        'session_id',
        'test-session-id-abc'
      );
      expect(localStorage.setItem).toHaveBeenCalledWith(
        'negotiate_response',
        JSON.stringify(mockNegotiateResponse)
      );
      expect(router.navigate).toHaveBeenCalledWith([
        '/brief',
        'test-session-id-abc',
      ]);
    });

    it('should set error message and stop submitting on negotiate failure', () => {
      apiSpy.negotiate.and.returnValue(
        throwError(() => new Error('Server error'))
      );

      component.onSubmit();

      expect(component.error).toBe(
        'Negotiation request failed. Please try again.'
      );
      expect(component.submitting).toBeFalse();
    });
  });

  describe('template renders NegotiateResponse fields', () => {
    it('should display tower info fields in the template', () => {
      configureTestBed('ATT-FL-4205');
      apiSpy.getTowers.and.returnValue(
        of({ towers: [mockTower], count: 1 })
      );

      fixture = TestBed.createComponent(TowerDetailComponent);
      component = fixture.componentInstance;
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      // Verify tower_id badge is rendered
      expect(compiled.querySelector('.tower-id-badge')?.textContent).toContain(
        'ATT-FL-4205'
      );
      // Verify nickname is rendered
      expect(compiled.querySelector('h2')?.textContent).toContain(
        'Tampa Bay Ground Mount'
      );
    });
  });
});
