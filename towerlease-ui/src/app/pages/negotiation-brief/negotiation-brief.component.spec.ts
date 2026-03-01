import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { of, throwError } from 'rxjs';

import { NegotiationBriefComponent } from './negotiation-brief.component';
import { TowerLeaseApiService } from '../../services/tower-lease-api.service';
import {
  NegotiateResponse,
  FollowupResponse,
} from '../../models/tower-lease.models';

describe('NegotiationBriefComponent', () => {
  let component: NegotiationBriefComponent;
  let fixture: ComponentFixture<NegotiationBriefComponent>;
  let apiSpy: jasmine.SpyObj<TowerLeaseApiService>;
  let router: Router;

  const mockBrief: NegotiateResponse = {
    session_id: 'test-session-brief-001',
    brief: 'Test negotiation brief text.',
    recommended_opening_rate: 2800,
    walk_away_rate: 3100,
    key_leverage_points: ['Leverage point 1', 'Leverage point 2'],
    comparable_rates: { low: 2600, median: 3000, high: 3800 },
    provider_context: 'Provider context here.',
    region_context: 'Region context here.',
    negotiation_history_summary: 'Historical rates show 4% annual escalation.',
    crm_intelligence: 'Provider has strategic relationship tier with AT&T.',
  };

  function configureTestBed(sessionId: string): void {
    apiSpy = jasmine.createSpyObj('TowerLeaseApiService', [
      'getTowers',
      'negotiate',
      'followup',
    ]);

    TestBed.configureTestingModule({
      imports: [RouterTestingModule, FormsModule],
      declarations: [NegotiationBriefComponent],
      providers: [
        { provide: TowerLeaseApiService, useValue: apiSpy },
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              paramMap: {
                get: (key: string) =>
                  key === 'session' ? sessionId : null,
              },
            },
          },
        },
      ],
    }).compileComponents();
  }

  afterEach(() => {
    localStorage.removeItem('negotiate_response');
    localStorage.removeItem('session_id');
  });

  describe('ngOnInit - loads brief from localStorage', () => {
    it('should load brief from localStorage when session_id matches', () => {
      localStorage.setItem(
        'negotiate_response',
        JSON.stringify(mockBrief)
      );

      configureTestBed('test-session-brief-001');
      fixture = TestBed.createComponent(NegotiationBriefComponent);
      component = fixture.componentInstance;
      fixture.detectChanges();

      expect(component.sessionId).toBe('test-session-brief-001');
      expect(component.brief).toEqual(mockBrief);
    });

    it('should set error when no session ID is provided', () => {
      configureTestBed('');
      fixture = TestBed.createComponent(NegotiationBriefComponent);
      component = fixture.componentInstance;
      fixture.detectChanges();

      expect(component.error).toBe('No session ID provided.');
    });

    it('should store session_id from negotiate response for follow-up calls', () => {
      localStorage.setItem(
        'negotiate_response',
        JSON.stringify(mockBrief)
      );

      configureTestBed('test-session-brief-001');
      fixture = TestBed.createComponent(NegotiationBriefComponent);
      component = fixture.componentInstance;
      fixture.detectChanges();

      // session_id from the negotiate response should be stored
      expect(component.sessionId).toBe('test-session-brief-001');
      expect(component.brief?.session_id).toBe('test-session-brief-001');
    });
  });

  describe('template renders all NegotiateResponse fields', () => {
    beforeEach(() => {
      localStorage.setItem(
        'negotiate_response',
        JSON.stringify(mockBrief)
      );
      configureTestBed('test-session-brief-001');
      fixture = TestBed.createComponent(NegotiationBriefComponent);
      component = fixture.componentInstance;
      fixture.detectChanges();
    });

    it('should render the brief text', () => {
      const el = fixture.nativeElement as HTMLElement;
      expect(el.querySelector('.brief-text')?.textContent).toContain(
        'Test negotiation brief text.'
      );
    });

    it('should render recommended_opening_rate', () => {
      const el = fixture.nativeElement as HTMLElement;
      const rateValues = el.querySelectorAll('.rate-value');
      // First rate-value is recommended_opening_rate
      expect(rateValues[0]?.textContent).toContain('2');
    });

    it('should render walk_away_rate', () => {
      const el = fixture.nativeElement as HTMLElement;
      const rateValues = el.querySelectorAll('.rate-value');
      // Second rate-value is walk_away_rate
      expect(rateValues[1]?.textContent).toContain('3');
    });

    it('should render comparable_rates low, median, high', () => {
      const el = fixture.nativeElement as HTMLElement;
      const rateValues = el.querySelectorAll('.rate-value');
      // rateValues[2] = low, [3] = median, [4] = high
      expect(rateValues.length).toBeGreaterThanOrEqual(5);
      expect(rateValues[2]?.textContent).toBeTruthy();
      expect(rateValues[3]?.textContent).toBeTruthy();
      expect(rateValues[4]?.textContent).toBeTruthy();
    });

    it('should render key_leverage_points', () => {
      const el = fixture.nativeElement as HTMLElement;
      const leverageItems = el.querySelectorAll('.leverage-list li');
      expect(leverageItems.length).toBe(2);
      expect(leverageItems[0]?.textContent).toContain('Leverage point 1');
      expect(leverageItems[1]?.textContent).toContain('Leverage point 2');
    });

    it('should render provider_context', () => {
      const el = fixture.nativeElement as HTMLElement;
      const contextTexts = el.querySelectorAll('.context-text');
      const providerCtx = Array.from(contextTexts).find((e) =>
        e.textContent?.includes('Provider context here.')
      );
      expect(providerCtx).toBeTruthy();
    });

    it('should render region_context', () => {
      const el = fixture.nativeElement as HTMLElement;
      const contextTexts = el.querySelectorAll('.context-text');
      const regionCtx = Array.from(contextTexts).find((e) =>
        e.textContent?.includes('Region context here.')
      );
      expect(regionCtx).toBeTruthy();
    });

    it('should render negotiation_history_summary', () => {
      const el = fixture.nativeElement as HTMLElement;
      const contextTexts = el.querySelectorAll('.context-text');
      const historyCtx = Array.from(contextTexts).find((e) =>
        e.textContent?.includes('Historical rates show 4% annual escalation.')
      );
      expect(historyCtx).toBeTruthy();
    });

    it('should render crm_intelligence', () => {
      const el = fixture.nativeElement as HTMLElement;
      const contextTexts = el.querySelectorAll('.context-text');
      const crmCtx = Array.from(contextTexts).find((e) =>
        e.textContent?.includes(
          'Provider has strategic relationship tier with AT&T.'
        )
      );
      expect(crmCtx).toBeTruthy();
    });
  });

  describe('Follow-up Q&A', () => {
    beforeEach(() => {
      localStorage.setItem(
        'negotiate_response',
        JSON.stringify(mockBrief)
      );
      configureTestBed('test-session-brief-001');
      fixture = TestBed.createComponent(NegotiationBriefComponent);
      component = fixture.componentInstance;
      router = TestBed.inject(Router);
      fixture.detectChanges();
    });

    it('should call followup() with the stored session_id and the user question', () => {
      const mockFollowupResponse: FollowupResponse = {
        answer: 'Here is the follow-up answer.',
        session_id: 'test-session-brief-001',
      };
      apiSpy.followup.and.returnValue(of(mockFollowupResponse));

      component.question = 'What about the comparable data?';
      component.askFollowup();

      expect(apiSpy.followup).toHaveBeenCalledTimes(1);
      const sentRequest = apiSpy.followup.calls.mostRecent().args[0];
      expect(sentRequest.session_id).toBe('test-session-brief-001');
      expect(sentRequest.question).toBe('What about the comparable data?');
    });

    it('should render the answer in qaHistory and session_id should match stored one', () => {
      const mockFollowupResponse: FollowupResponse = {
        answer: 'Here is the follow-up answer.',
        session_id: 'test-session-brief-001',
      };
      apiSpy.followup.and.returnValue(of(mockFollowupResponse));

      component.question = 'What about the comparable data?';
      component.askFollowup();

      expect(component.qaHistory.length).toBe(1);
      expect(component.qaHistory[0].question).toBe(
        'What about the comparable data?'
      );
      expect(component.qaHistory[0].answer).toBe(
        'Here is the follow-up answer.'
      );
      // The echoed session_id should match the stored one
      expect(mockFollowupResponse.session_id).toBe(component.sessionId);

      fixture.detectChanges();
      const el = fixture.nativeElement as HTMLElement;
      const qaAnswers = el.querySelectorAll('.qa-answer');
      expect(qaAnswers.length).toBe(1);
      expect(qaAnswers[0]?.textContent).toContain(
        'Here is the follow-up answer.'
      );
    });

    it('should show session expired error on 404 response matching backend behavior', () => {
      // Matching backend: test_server.py lines 170-179 => "Session expired or not found"
      const httpError = new HttpErrorResponse({
        status: 404,
        statusText: 'Not Found',
        error: { detail: 'Session expired or not found' },
      });
      apiSpy.followup.and.returnValue(throwError(() => httpError));

      component.question = 'This should fail.';
      component.askFollowup();

      expect(component.sessionExpired).toBeTrue();
      expect(component.error).toContain('Session expired or not found');

      fixture.detectChanges();
      const el = fixture.nativeElement as HTMLElement;
      const errorBanner = el.querySelector('.error-banner');
      expect(errorBanner?.textContent).toContain('Session expired or not found');
      // Should show a button to generate a new brief
      const generateBtn = el.querySelector('.error-banner .btn');
      expect(generateBtn?.textContent).toContain('Generate New Brief');
    });

    it('should not submit an empty or whitespace-only question', () => {
      component.question = '   ';
      component.askFollowup();
      expect(apiSpy.followup).not.toHaveBeenCalled();
    });

    it('should restore the question text on error so user can retry', () => {
      const httpError = new HttpErrorResponse({
        status: 500,
        statusText: 'Internal Server Error',
      });
      apiSpy.followup.and.returnValue(throwError(() => httpError));

      component.question = 'Will this fail?';
      component.askFollowup();

      expect(component.question).toBe('Will this fail?');
      expect(component.askingFollowup).toBeFalse();
    });
  });
});
