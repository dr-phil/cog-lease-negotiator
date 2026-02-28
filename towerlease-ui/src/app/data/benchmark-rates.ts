export interface RateBand {
  low: number;
  median: number;
  high: number;
}

export interface RegionBenchmarks {
  [towerType: string]: RateBand;
}

export const BENCHMARK_RATES: { [region: string]: RegionBenchmarks } = {
  northeast: {
    rooftop:      { low: 12000, median: 18000, high: 28000 },
    ground_mount: { low: 2200,  median: 3400,  high: 5000 },
    water_tower:  { low: 3800,  median: 5500,  high: 8000 },
    monopole:     { low: 2800,  median: 4200,  high: 6200 },
  },
  southeast: {
    rooftop:      { low: 8000,  median: 12000, high: 19000 },
    ground_mount: { low: 1600,  median: 2600,  high: 4000 },
    water_tower:  { low: 2800,  median: 4200,  high: 6200 },
    monopole:     { low: 2200,  median: 3400,  high: 5000 },
  },
  midwest: {
    rooftop:      { low: 6000,  median: 9500,  high: 15000 },
    ground_mount: { low: 1200,  median: 2000,  high: 3200 },
    water_tower:  { low: 2000,  median: 3200,  high: 4800 },
    monopole:     { low: 1600,  median: 2600,  high: 3800 },
  },
  west: {
    rooftop:      { low: 10000, median: 16000, high: 25000 },
    ground_mount: { low: 2000,  median: 3000,  high: 4500 },
    water_tower:  { low: 3200,  median: 4800,  high: 7000 },
    monopole:     { low: 2400,  median: 3800,  high: 5600 },
  },
};

export const REGIONS = ['northeast', 'southeast', 'midwest', 'west'] as const;
export const TOWER_TYPES = ['rooftop', 'monopole', 'ground_mount', 'water_tower'] as const;
