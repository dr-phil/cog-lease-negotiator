import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { TowerLeaseApiService } from '../../services/tower-lease-api.service';
import { TowerInfo } from '../../models/tower-lease.models';
import { TOWER_INVENTORY } from '../../data/tower-inventory';

@Component({
  selector: 'app-tower-list',
  templateUrl: './tower-list.component.html',
  styleUrls: ['./tower-list.component.scss'],
})
export class TowerListComponent implements OnInit {
  towers: TowerInfo[] = [];
  filteredTowers: TowerInfo[] = [];
  loading = true;
  error = '';

  // Filter values
  providerFilter = '';
  regionFilter = '';
  towerTypeFilter = '';

  // Unique filter options
  providers: string[] = [];
  regions: string[] = [];
  towerTypes: string[] = [];

  // Sort state
  sortColumn = '';
  sortDirection: 'asc' | 'desc' = 'asc';

  constructor(
    private api: TowerLeaseApiService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.api.getTowers().subscribe({
      next: (res) => {
        this.towers = res.towers;
        this.providers = [...new Set(res.towers.map((t) => t.provider))].sort();
        this.regions = [...new Set(res.towers.map((t) => t.region))].sort();
        this.towerTypes = [...new Set(res.towers.map((t) => t.tower_type))].sort();
        this.applyFilters();
        this.loading = false;
      },
      error: () => {
        // Fall back to hardcoded inventory when backend is unavailable
        this.towers = TOWER_INVENTORY;
        this.providers = [...new Set(this.towers.map((t) => t.provider))].sort();
        this.regions = [...new Set(this.towers.map((t) => t.region))].sort();
        this.towerTypes = [...new Set(this.towers.map((t) => t.tower_type))].sort();
        this.applyFilters();
        this.loading = false;
      },
    });
  }

  applyFilters(): void {
    this.filteredTowers = this.towers.filter((t) => {
      const matchProvider = !this.providerFilter || t.provider === this.providerFilter;
      const matchRegion = !this.regionFilter || t.region === this.regionFilter;
      const matchType = !this.towerTypeFilter || t.tower_type === this.towerTypeFilter;
      return matchProvider && matchRegion && matchType;
    });
    if (this.sortColumn) {
      this.sortBy(this.sortColumn, false);
    }
  }

  sortBy(column: string, toggle = true): void {
    if (toggle) {
      if (this.sortColumn === column) {
        this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortColumn = column;
        this.sortDirection = 'asc';
      }
    }
    this.filteredTowers.sort((a, b) => {
      const valA = (a as unknown as Record<string, unknown>)[this.sortColumn];
      const valB = (b as unknown as Record<string, unknown>)[this.sortColumn];
      let comparison = 0;
      if (typeof valA === 'number' && typeof valB === 'number') {
        comparison = valA - valB;
      } else {
        comparison = String(valA).localeCompare(String(valB));
      }
      return this.sortDirection === 'asc' ? comparison : -comparison;
    });
  }

  getRowClass(tower: TowerInfo): string {
    const expiry = new Date(tower.lease_expiry);
    const now = new Date();
    const monthsRemaining =
      (expiry.getFullYear() - now.getFullYear()) * 12 +
      (expiry.getMonth() - now.getMonth());
    if (monthsRemaining <= 6) return 'urgency-red';
    if (monthsRemaining <= 12) return 'urgency-yellow';
    return 'urgency-green';
  }

  getSortIcon(column: string): string {
    if (this.sortColumn !== column) return '';
    return this.sortDirection === 'asc' ? ' ▲' : ' ▼';
  }

  formatProvider(provider: string): string {
    return provider.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  }

  formatRate(rate: number): string {
    return '$' + rate.toLocaleString();
  }

  onNegotiate(tower: TowerInfo): void {
    this.router.navigate(['/towers', tower.tower_id]);
  }
}
