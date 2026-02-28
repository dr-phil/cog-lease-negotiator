export type RiskLevel = 'low' | 'moderate' | 'elevated';

export interface RegulatoryCell {
  risk_level: RiskLevel;
  estimated_new_site_timeline_months: number;
  statutes: string[];
  pending_legislation: string;
}

export const PENDING_LEGISLATION_STRINGS: string[] = [
  'State bill to reduce tower permit review timeline from 150 to 90 days -- committee vote pending',
  'Proposed legislation to exempt 5G small cells from local zoning review entirely',
  'County considering moratorium on new tower construction pending updated comprehensive plan',
  'State wireless infrastructure modernization act -- would streamline permitting statewide',
];

export const REGULATORY_MATRIX: { [region: string]: { [towerType: string]: RegulatoryCell } } = {
  northeast: {
    rooftop: {
      risk_level: 'elevated',
      estimated_new_site_timeline_months: 14,
      statutes: ['NYC Zoning Resolution Section 22-13', 'FAA Part 77 height restrictions'],
      pending_legislation: PENDING_LEGISLATION_STRINGS[0],
    },
    monopole: {
      risk_level: 'moderate',
      estimated_new_site_timeline_months: 10,
      statutes: ['State Telecommunications Act Section 5A', 'Local permitting ordinance 2021-34'],
      pending_legislation: PENDING_LEGISLATION_STRINGS[1],
    },
    ground_mount: {
      risk_level: 'moderate',
      estimated_new_site_timeline_months: 8,
      statutes: ['Federal Telecommunications Act Section 332(c)(7)', 'NEPA environmental review'],
      pending_legislation: PENDING_LEGISLATION_STRINGS[3],
    },
    water_tower: {
      risk_level: 'low',
      estimated_new_site_timeline_months: 6,
      statutes: ['Municipal colocation ordinance 2020-18', 'SHPO historic review waiver'],
      pending_legislation: PENDING_LEGISLATION_STRINGS[3],
    },
  },
  southeast: {
    rooftop: {
      risk_level: 'moderate',
      estimated_new_site_timeline_months: 10,
      statutes: ['State building code Section 14.2', 'FAA Part 77 height restrictions'],
      pending_legislation: PENDING_LEGISLATION_STRINGS[3],
    },
    monopole: {
      risk_level: 'low',
      estimated_new_site_timeline_months: 6,
      statutes: ['Streamlined permitting under SB-201', 'County right-of-way agreement'],
      pending_legislation: PENDING_LEGISLATION_STRINGS[1],
    },
    ground_mount: {
      risk_level: 'low',
      estimated_new_site_timeline_months: 5,
      statutes: ['Agricultural zoning exemption A-3', 'Federal Telecommunications Act Section 332(c)(7)'],
      pending_legislation: PENDING_LEGISLATION_STRINGS[2],
    },
    water_tower: {
      risk_level: 'moderate',
      estimated_new_site_timeline_months: 8,
      statutes: ['Municipal utility colocation policy', 'Environmental impact review requirement'],
      pending_legislation: PENDING_LEGISLATION_STRINGS[0],
    },
  },
  midwest: {
    rooftop: {
      risk_level: 'moderate',
      estimated_new_site_timeline_months: 9,
      statutes: ['City zoning ordinance Chapter 17', 'State historic preservation review'],
      pending_legislation: PENDING_LEGISLATION_STRINGS[0],
    },
    monopole: {
      risk_level: 'low',
      estimated_new_site_timeline_months: 5,
      statutes: ['Streamlined tower act HB-445', 'County road commission agreement'],
      pending_legislation: PENDING_LEGISLATION_STRINGS[3],
    },
    ground_mount: {
      risk_level: 'low',
      estimated_new_site_timeline_months: 4,
      statutes: ['Agricultural exemption clause', 'FCC shot clock compliance'],
      pending_legislation: PENDING_LEGISLATION_STRINGS[1],
    },
    water_tower: {
      risk_level: 'low',
      estimated_new_site_timeline_months: 5,
      statutes: ['Municipal colocation program 2022', 'State utility easement statute'],
      pending_legislation: PENDING_LEGISLATION_STRINGS[2],
    },
  },
  west: {
    rooftop: {
      risk_level: 'elevated',
      estimated_new_site_timeline_months: 16,
      statutes: ['CEQA environmental review', 'City building code Section 9.4', 'FAA Part 77'],
      pending_legislation: PENDING_LEGISLATION_STRINGS[2],
    },
    monopole: {
      risk_level: 'moderate',
      estimated_new_site_timeline_months: 11,
      statutes: ['State wireless facility siting act', 'BLM land use authorization'],
      pending_legislation: PENDING_LEGISLATION_STRINGS[0],
    },
    ground_mount: {
      risk_level: 'moderate',
      estimated_new_site_timeline_months: 9,
      statutes: ['County land use permit LU-2023-7', 'NEPA categorical exclusion review'],
      pending_legislation: PENDING_LEGISLATION_STRINGS[3],
    },
    water_tower: {
      risk_level: 'low',
      estimated_new_site_timeline_months: 7,
      statutes: ['Municipal colocation ordinance', 'State water utility infrastructure act'],
      pending_legislation: PENDING_LEGISLATION_STRINGS[1],
    },
  },
};

export const REGIONS = ['northeast', 'southeast', 'midwest', 'west'] as const;
export const TOWER_TYPES = ['rooftop', 'monopole', 'ground_mount', 'water_tower'] as const;
