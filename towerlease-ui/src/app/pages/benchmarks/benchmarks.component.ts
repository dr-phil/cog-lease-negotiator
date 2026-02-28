import { Component, OnInit, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { Chart, registerables } from 'chart.js';
import { BENCHMARK_RATES, REGIONS, TOWER_TYPES } from '../../data/benchmark-rates';

Chart.register(...registerables);

@Component({
  selector: 'app-benchmarks',
  templateUrl: './benchmarks.component.html',
  styleUrls: ['./benchmarks.component.scss'],
})
export class BenchmarksComponent implements AfterViewInit {
  @ViewChild('chartCanvas', { static: true }) chartCanvas!: ElementRef<HTMLCanvasElement>;

  regions = REGIONS;
  towerTypes = TOWER_TYPES;
  selectedRegion: string = 'northeast';
  private chart: Chart | null = null;

  ngAfterViewInit(): void {
    this.renderChart();
  }

  onRegionChange(region: string): void {
    this.selectedRegion = region;
    this.renderChart();
  }

  private renderChart(): void {
    if (this.chart) {
      this.chart.destroy();
    }

    const regionData = BENCHMARK_RATES[this.selectedRegion];
    const labels = this.towerTypes.map((t) => this.formatType(t));
    const lowData = this.towerTypes.map((t) => regionData[t].low);
    const medianData = this.towerTypes.map((t) => regionData[t].median);
    const highData = this.towerTypes.map((t) => regionData[t].high);

    this.chart = new Chart(this.chartCanvas.nativeElement, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'Low',
            data: lowData,
            backgroundColor: '#81c784',
          },
          {
            label: 'Median',
            data: medianData,
            backgroundColor: '#42a5f5',
          },
          {
            label: 'High',
            data: highData,
            backgroundColor: '#ef5350',
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: `${this.formatRegion(this.selectedRegion)} — Monthly Rate Benchmarks by Tower Type`,
            font: { size: 16 },
          },
          legend: {
            position: 'top',
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: (value) => '$' + Number(value).toLocaleString(),
            },
            title: {
              display: true,
              text: 'Monthly Rate ($)',
            },
          },
        },
      },
    });
  }

  formatType(type: string): string {
    return type.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  }

  formatRegion(region: string): string {
    return region.replace(/\b\w/g, (c) => c.toUpperCase());
  }
}
