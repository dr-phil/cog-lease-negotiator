export interface LeaseComparable {
  comp_id: string;
  address: string;
  distance_miles: number;
  monthly_rate: number;
  tower_type: string;
  lease_date: string;
  escalation_terms: string;
  provider: string;
  lease_term_years: number;
  region: string;
}

export const LEASE_COMPARABLES: LeaseComparable[] = [
  // Northeast
  {
    comp_id: 'NE-001', address: '245 Park Ave, New York, NY', distance_miles: 1.2,
    monthly_rate: 19200, tower_type: 'rooftop', lease_date: '2024-06-15',
    escalation_terms: '3% annual', provider: 'crown_castle', lease_term_years: 10, region: 'northeast',
  },
  {
    comp_id: 'NE-002', address: '88 Summer St, Boston, MA', distance_miles: 0.8,
    monthly_rate: 17500, tower_type: 'rooftop', lease_date: '2024-03-01',
    escalation_terms: '2.5% annual', provider: 'american_tower', lease_term_years: 7, region: 'northeast',
  },
  {
    comp_id: 'NE-003', address: '15 Asylum St, Hartford, CT', distance_miles: 2.5,
    monthly_rate: 10200, tower_type: 'rooftop', lease_date: '2023-11-20',
    escalation_terms: 'CPI-linked', provider: 'municipal', lease_term_years: 5, region: 'northeast',
  },
  {
    comp_id: 'NE-004', address: '400 Rt 9, Framingham, MA', distance_miles: 5.1,
    monthly_rate: 4800, tower_type: 'monopole', lease_date: '2024-01-10',
    escalation_terms: '3% annual', provider: 'crown_castle', lease_term_years: 10, region: 'northeast',
  },
  {
    comp_id: 'NE-005', address: '72 Industrial Blvd, Stamford, CT', distance_miles: 3.7,
    monthly_rate: 3600, tower_type: 'ground_mount', lease_date: '2024-08-22',
    escalation_terms: '2% annual', provider: 'sba_communications', lease_term_years: 15, region: 'northeast',
  },
  // Southeast
  {
    comp_id: 'SE-001', address: '1200 Peachtree St, Atlanta, GA', distance_miles: 1.8,
    monthly_rate: 13500, tower_type: 'rooftop', lease_date: '2024-04-12',
    escalation_terms: '3% annual', provider: 'crown_castle', lease_term_years: 10, region: 'southeast',
  },
  {
    comp_id: 'SE-002', address: '550 S Orange Ave, Orlando, FL', distance_miles: 2.3,
    monthly_rate: 3900, tower_type: 'monopole', lease_date: '2024-02-28',
    escalation_terms: '2.5% annual', provider: 'american_tower', lease_term_years: 7, region: 'southeast',
  },
  {
    comp_id: 'SE-003', address: '101 E Kennedy Blvd, Tampa, FL', distance_miles: 4.0,
    monthly_rate: 3100, tower_type: 'ground_mount', lease_date: '2023-09-15',
    escalation_terms: 'CPI-linked', provider: 'sba_communications', lease_term_years: 10, region: 'southeast',
  },
  {
    comp_id: 'SE-004', address: '300 W Morgan St, Durham, NC', distance_miles: 1.5,
    monthly_rate: 4500, tower_type: 'water_tower', lease_date: '2024-07-01',
    escalation_terms: '3% annual', provider: 'municipal', lease_term_years: 5, region: 'southeast',
  },
  {
    comp_id: 'SE-005', address: '800 Madison St, Huntsville, AL', distance_miles: 6.2,
    monthly_rate: 1800, tower_type: 'ground_mount', lease_date: '2024-05-18',
    escalation_terms: '2% annual', provider: 'rural_individual', lease_term_years: 20, region: 'southeast',
  },
  // Midwest
  {
    comp_id: 'MW-001', address: '233 S Wacker Dr, Chicago, IL', distance_miles: 0.9,
    monthly_rate: 12800, tower_type: 'rooftop', lease_date: '2024-01-22',
    escalation_terms: '3% annual', provider: 'american_tower', lease_term_years: 10, region: 'midwest',
  },
  {
    comp_id: 'MW-002', address: '50 W Broad St, Columbus, OH', distance_miles: 2.0,
    monthly_rate: 2900, tower_type: 'monopole', lease_date: '2024-06-05',
    escalation_terms: '2.5% annual', provider: 'sba_communications', lease_term_years: 7, region: 'midwest',
  },
  {
    comp_id: 'MW-003', address: '125 Keystone Pkwy, Carmel, IN', distance_miles: 3.4,
    monthly_rate: 3400, tower_type: 'water_tower', lease_date: '2023-12-10',
    escalation_terms: 'CPI-linked', provider: 'municipal', lease_term_years: 5, region: 'midwest',
  },
  {
    comp_id: 'MW-004', address: '1st Ave NE, Cedar Rapids, IA', distance_miles: 7.8,
    monthly_rate: 1600, tower_type: 'ground_mount', lease_date: '2024-03-30',
    escalation_terms: '2% annual', provider: 'rural_individual', lease_term_years: 20, region: 'midwest',
  },
  {
    comp_id: 'MW-005', address: '400 N Michigan Ave, Chicago, IL', distance_miles: 1.5,
    monthly_rate: 10500, tower_type: 'rooftop', lease_date: '2024-09-01',
    escalation_terms: '3% annual', provider: 'crown_castle', lease_term_years: 10, region: 'midwest',
  },
  // West (set 1)
  {
    comp_id: 'W-001', address: '101 Market St, San Francisco, CA', distance_miles: 1.0,
    monthly_rate: 22000, tower_type: 'rooftop', lease_date: '2024-05-10',
    escalation_terms: '3% annual', provider: 'crown_castle', lease_term_years: 10, region: 'west',
  },
  {
    comp_id: 'W-002', address: '3500 N Central Ave, Phoenix, AZ', distance_miles: 2.8,
    monthly_rate: 4100, tower_type: 'monopole', lease_date: '2024-02-14',
    escalation_terms: '2.5% annual', provider: 'sba_communications', lease_term_years: 7, region: 'west',
  },
  {
    comp_id: 'W-003', address: '1515 Rimrock Rd, Billings, MT', distance_miles: 8.5,
    monthly_rate: 1900, tower_type: 'ground_mount', lease_date: '2024-04-20',
    escalation_terms: '2% annual', provider: 'rural_individual', lease_term_years: 20, region: 'west',
  },
  {
    comp_id: 'W-004', address: '600 Pine St, Seattle, WA', distance_miles: 3.2,
    monthly_rate: 18500, tower_type: 'rooftop', lease_date: '2023-10-15',
    escalation_terms: 'CPI-linked', provider: 'american_tower', lease_term_years: 10, region: 'west',
  },
  {
    comp_id: 'W-005', address: '200 S Virginia St, Reno, NV', distance_miles: 5.5,
    monthly_rate: 3200, tower_type: 'ground_mount', lease_date: '2024-07-30',
    escalation_terms: '2.5% annual', provider: 'crown_castle', lease_term_years: 15, region: 'west',
  },
  // West (set 2 - additional)
  {
    comp_id: 'W-006', address: '700 Wilshire Blvd, Los Angeles, CA', distance_miles: 4.1,
    monthly_rate: 20500, tower_type: 'rooftop', lease_date: '2024-08-05',
    escalation_terms: '3% annual', provider: 'american_tower', lease_term_years: 10, region: 'west',
  },
  {
    comp_id: 'W-007', address: '1000 E Apache Blvd, Tempe, AZ', distance_miles: 6.0,
    monthly_rate: 3500, tower_type: 'monopole', lease_date: '2024-01-18',
    escalation_terms: '2% annual', provider: 'sba_communications', lease_term_years: 7, region: 'west',
  },
  {
    comp_id: 'W-008', address: '450 Broadway, Denver, CO', distance_miles: 2.2,
    monthly_rate: 15200, tower_type: 'rooftop', lease_date: '2024-06-22',
    escalation_terms: '3% annual', provider: 'crown_castle', lease_term_years: 10, region: 'west',
  },
  {
    comp_id: 'W-009', address: '300 Main St, Boise, ID', distance_miles: 9.0,
    monthly_rate: 2500, tower_type: 'ground_mount', lease_date: '2024-03-12',
    escalation_terms: 'CPI-linked', provider: 'rural_individual', lease_term_years: 15, region: 'west',
  },
  {
    comp_id: 'W-010', address: '55 S Main St, Salt Lake City, UT', distance_miles: 3.8,
    monthly_rate: 5200, tower_type: 'water_tower', lease_date: '2024-09-10',
    escalation_terms: '2.5% annual', provider: 'municipal', lease_term_years: 5, region: 'west',
  },
];
