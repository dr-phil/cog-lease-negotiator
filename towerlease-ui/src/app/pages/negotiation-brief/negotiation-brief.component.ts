import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';
import { TowerLeaseApiService } from '../../services/tower-lease-api.service';
import { NegotiateResponse } from '../../models/tower-lease.models';

interface QAPair {
  question: string;
  answer: string;
}

@Component({
  selector: 'app-negotiation-brief',
  templateUrl: './negotiation-brief.component.html',
  styleUrls: ['./negotiation-brief.component.scss'],
})
export class NegotiationBriefComponent implements OnInit {
  sessionId = '';
  brief: NegotiateResponse | null = null;
  error = '';
  sessionExpired = false;

  // Follow-up Q&A
  question = '';
  askingFollowup = false;
  qaHistory: QAPair[] = [];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private api: TowerLeaseApiService
  ) {}

  ngOnInit(): void {
    this.sessionId = this.route.snapshot.paramMap.get('session') || '';

    // Try to load from localStorage
    const stored = localStorage.getItem('negotiate_response');
    if (stored) {
      try {
        const parsed: NegotiateResponse = JSON.parse(stored);
        if (parsed.session_id === this.sessionId) {
          this.brief = parsed;
          return;
        }
      } catch {
        // ignore parse errors
      }
    }

    if (!this.sessionId) {
      this.error = 'No session ID provided.';
    }
  }

  formatRate(rate: number): string {
    return '$' + rate.toLocaleString();
  }

  getBarWidth(value: number, max: number): number {
    return Math.min((value / max) * 100, 100);
  }

  getMaxRate(): number {
    if (!this.brief) return 0;
    return Math.max(
      this.brief.recommended_opening_rate,
      this.brief.walk_away_rate,
      this.brief.comparable_rates.high
    );
  }

  askFollowup(): void {
    if (!this.question.trim() || this.askingFollowup) return;

    this.askingFollowup = true;
    this.error = '';
    this.sessionExpired = false;

    const currentQuestion = this.question;
    this.question = '';

    this.api.followup({ session_id: this.sessionId, question: currentQuestion }).subscribe({
      next: (res) => {
        this.qaHistory.push({ question: currentQuestion, answer: res.answer });
        this.askingFollowup = false;
      },
      error: (err: HttpErrorResponse) => {
        if (err.status === 404) {
          this.sessionExpired = true;
          this.error = 'Session expired or not found — please generate a new brief.';
        } else {
          this.error = 'Failed to get follow-up answer. Please try again.';
        }
        this.question = currentQuestion;
        this.askingFollowup = false;
      },
    });
  }

  goToTowers(): void {
    this.router.navigate(['/towers']);
  }
}
