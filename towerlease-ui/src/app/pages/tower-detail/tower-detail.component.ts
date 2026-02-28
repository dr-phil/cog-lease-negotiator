import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { TowerLeaseApiService } from '../../services/tower-lease-api.service';
import { TowerInfo, NegotiateRequest } from '../../models/tower-lease.models';

@Component({
  selector: 'app-tower-detail',
  templateUrl: './tower-detail.component.html',
  styleUrls: ['./tower-detail.component.scss'],
})
export class TowerDetailComponent implements OnInit {
  tower: TowerInfo | null = null;
  loading = true;
  submitting = false;
  error = '';

  // Form fields
  currentMonthlyRate = 0;
  leaseExpiry = '';
  leaseYearsRemaining = 0;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private api: TowerLeaseApiService
  ) {}

  ngOnInit(): void {
    const towerId = this.route.snapshot.paramMap.get('id');
    if (!towerId) {
      this.error = 'No tower ID provided.';
      this.loading = false;
      return;
    }

    this.api.getTowers().subscribe({
      next: (res) => {
        const found = res.towers.find((t) => t.tower_id === towerId);
        if (!found) {
          this.error = `Tower "${towerId}" not found.`;
          this.loading = false;
          return;
        }
        this.tower = found;
        this.currentMonthlyRate = found.current_monthly_rate;
        this.leaseExpiry = found.lease_expiry;
        this.leaseYearsRemaining = this.calculateYearsRemaining(found.lease_expiry);
        this.loading = false;
      },
      error: () => {
        this.error = 'Failed to load tower data. Please try again.';
        this.loading = false;
      },
    });
  }

  private calculateYearsRemaining(expiry: string): number {
    const expiryDate = new Date(expiry);
    const now = new Date();
    const diffMs = expiryDate.getTime() - now.getTime();
    const years = diffMs / (1000 * 60 * 60 * 24 * 365.25);
    return Math.round(years * 10) / 10;
  }

  formatProvider(provider: string): string {
    return provider.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  }

  onSubmit(): void {
    if (!this.tower) return;

    this.submitting = true;
    this.error = '';

    const request: NegotiateRequest = {
      tower_id: this.tower.tower_id,
      provider: this.tower.provider,
      region: this.tower.region,
      current_monthly_rate: this.currentMonthlyRate,
      lease_expiry: this.leaseExpiry,
      lease_years_remaining: this.leaseYearsRemaining,
    };

    this.api.negotiate(request).subscribe({
      next: (res) => {
        localStorage.setItem('session_id', res.session_id);
        localStorage.setItem('negotiate_response', JSON.stringify(res));
        this.router.navigate(['/brief', res.session_id]);
      },
      error: (err) => {
        this.error = 'Negotiation request failed. Please try again.';
        this.submitting = false;
      },
    });
  }

  goBack(): void {
    this.router.navigate(['/towers']);
  }
}
