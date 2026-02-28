export interface TowerUtilization {
  tower_id: string;
  nickname: string;
  provider: string;
  region: string;
  tower_type: string;
  occupied_slots: number;
  total_tenant_slots: number;
  bandwidth_utilization_pct: number;
  structural_capacity_remaining_pct: number;
  last_structural_inspection: string;
}

export const TOWER_UTILIZATION: TowerUtilization[] = [
  {
    tower_id: 'ATT-NY-1201', nickname: 'Midtown East Rooftop', provider: 'crown_castle',
    region: 'northeast', tower_type: 'rooftop',
    occupied_slots: 4, total_tenant_slots: 5, bandwidth_utilization_pct: 88,
    structural_capacity_remaining_pct: 25, last_structural_inspection: '2025-03-15',
  },
  {
    tower_id: 'ATT-GA-3302', nickname: 'Peachtree Industrial', provider: 'crown_castle',
    region: 'southeast', tower_type: 'monopole',
    occupied_slots: 3, total_tenant_slots: 4, bandwidth_utilization_pct: 72,
    structural_capacity_remaining_pct: 35, last_structural_inspection: '2025-01-20',
  },
  {
    tower_id: 'ATT-CA-7701', nickname: 'Bay Area Ground Site', provider: 'crown_castle',
    region: 'west', tower_type: 'ground_mount',
    occupied_slots: 2, total_tenant_slots: 4, bandwidth_utilization_pct: 55,
    structural_capacity_remaining_pct: 60, last_structural_inspection: '2024-11-10',
  },
  {
    tower_id: 'ATT-MA-1502', nickname: 'Boston Harbor Rooftop', provider: 'american_tower',
    region: 'northeast', tower_type: 'rooftop',
    occupied_slots: 5, total_tenant_slots: 5, bandwidth_utilization_pct: 94,
    structural_capacity_remaining_pct: 20, last_structural_inspection: '2025-04-01',
  },
  {
    tower_id: 'ATT-FL-4101', nickname: 'Orlando East Monopole', provider: 'american_tower',
    region: 'southeast', tower_type: 'monopole',
    occupied_slots: 2, total_tenant_slots: 5, bandwidth_utilization_pct: 48,
    structural_capacity_remaining_pct: 55, last_structural_inspection: '2025-02-18',
  },
  {
    tower_id: 'ATT-IL-5501', nickname: 'Chicago West Loop', provider: 'american_tower',
    region: 'midwest', tower_type: 'rooftop',
    occupied_slots: 4, total_tenant_slots: 5, bandwidth_utilization_pct: 82,
    structural_capacity_remaining_pct: 30, last_structural_inspection: '2025-05-12',
  },
  {
    tower_id: 'ATT-FL-4205', nickname: 'Tampa Bay Ground Mount', provider: 'sba_communications',
    region: 'southeast', tower_type: 'ground_mount',
    occupied_slots: 1, total_tenant_slots: 4, bandwidth_utilization_pct: 42,
    structural_capacity_remaining_pct: 70, last_structural_inspection: '2024-09-28',
  },
  {
    tower_id: 'ATT-OH-6001', nickname: 'Columbus Westside', provider: 'sba_communications',
    region: 'midwest', tower_type: 'monopole',
    occupied_slots: 3, total_tenant_slots: 4, bandwidth_utilization_pct: 67,
    structural_capacity_remaining_pct: 40, last_structural_inspection: '2025-01-05',
  },
  {
    tower_id: 'ATT-AZ-8101', nickname: 'Phoenix North Monopole', provider: 'sba_communications',
    region: 'west', tower_type: 'monopole',
    occupied_slots: 2, total_tenant_slots: 5, bandwidth_utilization_pct: 51,
    structural_capacity_remaining_pct: 50, last_structural_inspection: '2024-12-14',
  },
  {
    tower_id: 'ATT-IN-5801', nickname: 'Carmel Water Tower', provider: 'municipal',
    region: 'midwest', tower_type: 'water_tower',
    occupied_slots: 3, total_tenant_slots: 4, bandwidth_utilization_pct: 73,
    structural_capacity_remaining_pct: 38, last_structural_inspection: '2025-06-01',
  },
  {
    tower_id: 'ATT-NC-3501', nickname: 'Durham Municipal Tower', provider: 'municipal',
    region: 'southeast', tower_type: 'water_tower',
    occupied_slots: 2, total_tenant_slots: 3, bandwidth_utilization_pct: 61,
    structural_capacity_remaining_pct: 45, last_structural_inspection: '2025-03-22',
  },
  {
    tower_id: 'ATT-CT-1301', nickname: 'Hartford City Rooftop', provider: 'municipal',
    region: 'northeast', tower_type: 'rooftop',
    occupied_slots: 3, total_tenant_slots: 5, bandwidth_utilization_pct: 76,
    structural_capacity_remaining_pct: 42, last_structural_inspection: '2024-10-30',
  },
  {
    tower_id: 'ATT-IA-5901', nickname: 'Cedar Rapids Farm Site', provider: 'rural_individual',
    region: 'midwest', tower_type: 'ground_mount',
    occupied_slots: 1, total_tenant_slots: 3, bandwidth_utilization_pct: 40,
    structural_capacity_remaining_pct: 65, last_structural_inspection: '2024-08-15',
  },
  {
    tower_id: 'ATT-MT-8501', nickname: 'Billings Ranch Ground', provider: 'rural_individual',
    region: 'west', tower_type: 'ground_mount',
    occupied_slots: 1, total_tenant_slots: 3, bandwidth_utilization_pct: 44,
    structural_capacity_remaining_pct: 68, last_structural_inspection: '2024-07-20',
  },
  {
    tower_id: 'ATT-AL-3701', nickname: 'Huntsville Rural Site', provider: 'rural_individual',
    region: 'southeast', tower_type: 'ground_mount',
    occupied_slots: 2, total_tenant_slots: 3, bandwidth_utilization_pct: 58,
    structural_capacity_remaining_pct: 52, last_structural_inspection: '2025-02-05',
  },
];

export function getLeverageScore(occupiedSlots: number): 'High' | 'Moderate' | 'Low' {
  if (occupiedSlots >= 4) return 'High';
  if (occupiedSlots >= 3) return 'Moderate';
  return 'Low';
}

export function getLeverageNote(occupiedSlots: number): string {
  if (occupiedSlots >= 3) {
    return 'High occupancy increases AT&T leverage';
  }
  return 'Moderate occupancy — tower owner may seek to attract additional tenants';
}
