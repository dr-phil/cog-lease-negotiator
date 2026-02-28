import { Component, OnInit, ElementRef, ViewChildren, QueryList, AfterViewInit } from '@angular/core';
import { Chart, registerables } from 'chart.js';
import { TOWER_UTILIZATION, TowerUtilization, getLeverageScore, getLeverageNote } from '../../data/utilization-data';

Chart.register(...registerables);

@Component({
  selector: 'app-utilization',
  templateUrl: './utilization.component.html',
  styleUrls: ['./utilization.component.scss'],
})
export class UtilizationComponent implements AfterViewInit {
  towers = TOWER_UTILIZATION;
  private charts: Chart[] = [];

  ngAfterViewInit(): void {
    setTimeout(() => this.renderDonutCharts(), 100);
  }

  getLeverageScore(occupied: number): string {
    return getLeverageScore(occupied);
  }

  getLeverageNote(occupied: number): string {
    return getLeverageNote(occupied);
  }

  getLeverageBadgeClass(occupied: number): string {
    const score = getLeverageScore(occupied);
    switch (score) {
      case 'High': return 'badge-high';
      case 'Moderate': return 'badge-moderate';
      default: return 'badge-low';
    }
  }

  formatProvider(provider: string): string {
    return provider.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  }

  private renderDonutCharts(): void {
    this.charts.forEach((c) => c.destroy());
    this.charts = [];

    this.towers.forEach((tower, i) => {
      const canvas = document.getElementById('donut-' + i) as HTMLCanvasElement | null;
      if (!canvas) return;

      const chart = new Chart(canvas, {
        type: 'doughnut',
        data: {
          labels: ['Occupied', 'Available'],
          datasets: [{
            data: [tower.occupied_slots, tower.total_tenant_slots - tower.occupied_slots],
            backgroundColor: ['#1976d2', '#e0e0e0'],
            borderWidth: 0,
          }],
        },
        options: {
          responsive: false,
          plugins: {
            legend: { display: false },
            tooltip: { enabled: true },
          },
          cutout: '65%',
        },
      });
      this.charts.push(chart);
    });
  }
}
