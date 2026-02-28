import { Pipe, PipeTransform } from '@angular/core';
import { BENCHMARK_RATES } from '../../data/benchmark-rates';

@Pipe({ name: 'benchmarkRate' })
export class BenchmarkRatePipe implements PipeTransform {
  transform(region: string, towerType: string, band: string): number {
    const regionData = BENCHMARK_RATES[region];
    if (!regionData) return 0;
    const typeData = regionData[towerType];
    if (!typeData) return 0;
    if (band === 'low') return typeData.low;
    if (band === 'median') return typeData.median;
    if (band === 'high') return typeData.high;
    return 0;
  }
}
