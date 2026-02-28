import { Component, AfterViewInit, ViewChild, ElementRef } from '@angular/core';
import { Chart, registerables } from 'chart.js';
import { LEASE_COMPARABLES, LeaseComparable } from '../../data/comparables-data';

Chart.register(...registerables);

@Component({
  selector: 'app-comparables',
  templateUrl: './comparables.component.html',
  styleUrls: ['./comparables.component.scss'],
})
export class ComparablesComponent implements AfterViewInit {
  @ViewChild('scatterCanvas', { static: true }) scatterCanvas!: ElementRef<HTMLCanvasElement>;

  allComparables = LEASE_COMPARABLES;
  filteredComparables = LEASE_COMPARABLES;

  regionFilter = '';
  towerTypeFilter = '';
  providerFilter = '';

  regions = ['northeast', 'southeast', 'midwest', 'west'];
  towerTypes = ['rooftop', 'monopole', 'ground_mount', 'water_tower'];
  providers = ['crown_castle', 'american_tower', 'sba_communications', 'municipal', 'rural_individual'];

  private chart: Chart | null = null;

  ngAfterViewInit(): void {
    this.renderChart();
  }

  onFilterChange(): void {
    this.filteredComparables = this.allComparables.filter((c) => {
      if (this.regionFilter && c.region !== this.regionFilter) return false;
      if (this.towerTypeFilter && c.tower_type !== this.towerTypeFilter) return false;
      if (this.providerFilter && c.provider !== this.providerFilter) return false;
      return true;
    });
    this.renderChart();
  }

  private renderChart(): void {
    if (this.chart) {
      this.chart.destroy();
    }

    const data = this.filteredComparables.map((c) => ({
      x: c.distance_miles,
      y: c.monthly_rate,
    }));

    this.chart = new Chart(this.scatterCanvas.nativeElement, {
      type: 'scatter',
      data: {
        datasets: [{
          label: 'Lease Comparables',
          data,
          backgroundColor: '#1976d2',
          pointRadius: 6,
          pointHoverRadius: 8,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: 'Distance vs Monthly Rate',
            font: { size: 16 },
          },
        },
        scales: {
          x: {
            title: { display: true, text: 'Distance (miles)' },
            beginAtZero: true,
          },
          y: {
            title: { display: true, text: 'Monthly Rate ($)' },
            beginAtZero: true,
            ticks: {
              callback: (value) => '$' + Number(value).toLocaleString(),
            },
          },
        },
      },
    });
  }

  formatLabel(value: string): string {
    return value.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  }

  formatCurrency(value: number): string {
    return '$' + value.toLocaleString();
  }
}
