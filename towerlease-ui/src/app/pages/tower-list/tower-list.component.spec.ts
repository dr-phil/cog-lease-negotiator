import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { of, throwError } from 'rxjs';

import { TowerListComponent } from './tower-list.component';
import { TowerLeaseApiService } from '../../services/tower-lease-api.service';
import { TowerInfo } from '../../models/tower-lease.models';
import { TOWER_INVENTORY } from '../../data/tower-inventory';

describe('TowerListComponent', () => {
  let component: TowerListComponent;
  let fixture: ComponentFixture<TowerListComponent>;
  let apiSpy: jasmine.SpyObj<TowerLeaseApiService>;
  let router: Router;

  const mockTowers: TowerInfo[] = [
    {
      tower_id: 'ATT-NY-1201',
      nickname: 'Midtown East Rooftop',
      provider: 'crown_castle',
      region: 'northeast',
      tower_type: 'rooftop',
      current_monthly_rate: 18500,
      lease_expiry: '2025-11-01',
      coordinates: { lat: 40.7549, lng: -73.9724 },
    },
    {
      tower_id: 'ATT-FL-4205',
      nickname: 'Tampa Bay Ground Mount',
      provider: 'sba_communications',
      region: 'southeast',
      tower_type: 'ground_mount',
      current_monthly_rate: 3200,
      lease_expiry: '2025-07-01',
      coordinates: { lat: 27.9506, lng: -82.4572 },
    },
    {
      tower_id: 'ATT-IN-5801',
      nickname: 'Carmel Water Tower',
      provider: 'municipal',
      region: 'midwest',
      tower_type: 'water_tower',
      current_monthly_rate: 2400,
      lease_expiry: '2026-02-01',
      coordinates: { lat: 39.9784, lng: -86.118 },
    },
  ];

  beforeEach(async () => {
    apiSpy = jasmine.createSpyObj('TowerLeaseApiService', [
      'getTowers',
      'negotiate',
      'followup',
    ]);

    await TestBed.configureTestingModule({
      imports: [RouterTestingModule, FormsModule],
      declarations: [TowerListComponent],
      providers: [
        { provide: TowerLeaseApiService, useValue: apiSpy },
      ],
    }).compileComponents();

    router = TestBed.inject(Router);
    spyOn(router, 'navigate');
  });

  function createComponent(): void {
    fixture = TestBed.createComponent(TowerListComponent);
    component = fixture.componentInstance;
  }

  describe('ngOnInit - success path', () => {
    it('should call getTowers() and populate towers and filteredTowers from API response', () => {
      apiSpy.getTowers.and.returnValue(of({ towers: mockTowers, count: 3 }));
      createComponent();
      fixture.detectChanges();

      expect(apiSpy.getTowers).toHaveBeenCalled();
      expect(component.towers.length).toBe(3);
      expect(component.filteredTowers.length).toBe(3);
      expect(component.loading).toBeFalse();
    });

    it('should extract unique providers, regions, and towerTypes from the API response', () => {
      apiSpy.getTowers.and.returnValue(of({ towers: mockTowers, count: 3 }));
      createComponent();
      fixture.detectChanges();

      expect(component.providers).toContain('crown_castle');
      expect(component.providers).toContain('sba_communications');
      expect(component.providers).toContain('municipal');
      expect(component.regions).toContain('northeast');
      expect(component.regions).toContain('southeast');
      expect(component.regions).toContain('midwest');
      expect(component.towerTypes).toContain('rooftop');
      expect(component.towerTypes).toContain('ground_mount');
      expect(component.towerTypes).toContain('water_tower');
    });
  });

  describe('ngOnInit - error/fallback path', () => {
    it('should fall back to TOWER_INVENTORY when the API call fails', () => {
      apiSpy.getTowers.and.returnValue(throwError(() => new Error('Network error')));
      createComponent();
      fixture.detectChanges();

      expect(component.towers).toEqual(TOWER_INVENTORY);
      expect(component.filteredTowers.length).toBe(TOWER_INVENTORY.length);
      expect(component.loading).toBeFalse();
    });

    it('should contain all backend-expected provider enum values in TOWER_INVENTORY fallback', () => {
      // These must match backend values from test_server.py lines 50-55
      const expectedProviders = [
        'crown_castle',
        'american_tower',
        'sba_communications',
        'municipal',
        'rural_individual',
      ];
      const inventoryProviders = new Set(TOWER_INVENTORY.map((t) => t.provider));
      expectedProviders.forEach((p) => {
        expect(inventoryProviders.has(p))
          .withContext(`TOWER_INVENTORY missing provider: ${p}`)
          .toBeTrue();
      });
    });

    it('should contain all backend-expected region enum values in TOWER_INVENTORY fallback', () => {
      // These must match backend values from test_server.py lines 57-62
      const expectedRegions = ['northeast', 'southeast', 'midwest', 'west'];
      const inventoryRegions = new Set(TOWER_INVENTORY.map((t) => t.region));
      expectedRegions.forEach((r) => {
        expect(inventoryRegions.has(r))
          .withContext(`TOWER_INVENTORY missing region: ${r}`)
          .toBeTrue();
      });
    });

    it('should contain all backend-expected tower_type enum values in TOWER_INVENTORY fallback', () => {
      // These must match backend values from test_server.py lines 64-70
      const expectedTypes = ['rooftop', 'monopole', 'ground_mount', 'water_tower'];
      const inventoryTypes = new Set(TOWER_INVENTORY.map((t) => t.tower_type));
      expectedTypes.forEach((tt) => {
        expect(inventoryTypes.has(tt))
          .withContext(`TOWER_INVENTORY missing tower_type: ${tt}`)
          .toBeTrue();
      });
    });
  });

  describe('getRowClass()', () => {
    beforeEach(() => {
      apiSpy.getTowers.and.returnValue(of({ towers: [], count: 0 }));
      createComponent();
      fixture.detectChanges();
    });

    it('should return "urgency-red" for a tower expiring within 6 months', () => {
      const now = new Date();
      const threeMonthsLater = new Date(now.getFullYear(), now.getMonth() + 3, 1);
      const tower: TowerInfo = {
        ...mockTowers[0],
        lease_expiry: threeMonthsLater.toISOString().split('T')[0],
      };
      expect(component.getRowClass(tower)).toBe('urgency-red');
    });

    it('should return "urgency-red" for a tower expiring exactly 6 months from now', () => {
      const now = new Date();
      const sixMonthsLater = new Date(now.getFullYear(), now.getMonth() + 6, 1);
      const tower: TowerInfo = {
        ...mockTowers[0],
        lease_expiry: sixMonthsLater.toISOString().split('T')[0],
      };
      expect(component.getRowClass(tower)).toBe('urgency-red');
    });

    it('should return "urgency-yellow" for a tower expiring in 7-12 months', () => {
      const now = new Date();
      const nineMonthsLater = new Date(now.getFullYear(), now.getMonth() + 9, 1);
      const tower: TowerInfo = {
        ...mockTowers[0],
        lease_expiry: nineMonthsLater.toISOString().split('T')[0],
      };
      expect(component.getRowClass(tower)).toBe('urgency-yellow');
    });

    it('should return "urgency-yellow" for a tower expiring exactly 12 months from now', () => {
      const now = new Date();
      const twelveMonthsLater = new Date(now.getFullYear(), now.getMonth() + 12, 1);
      const tower: TowerInfo = {
        ...mockTowers[0],
        lease_expiry: twelveMonthsLater.toISOString().split('T')[0],
      };
      expect(component.getRowClass(tower)).toBe('urgency-yellow');
    });

    it('should return "urgency-green" for a tower expiring more than 12 months from now', () => {
      const now = new Date();
      const twoYearsLater = new Date(now.getFullYear() + 2, now.getMonth(), 1);
      const tower: TowerInfo = {
        ...mockTowers[0],
        lease_expiry: twoYearsLater.toISOString().split('T')[0],
      };
      expect(component.getRowClass(tower)).toBe('urgency-green');
    });

    it('should return "urgency-red" for an already-expired tower', () => {
      const tower: TowerInfo = {
        ...mockTowers[0],
        lease_expiry: '2020-01-01',
      };
      expect(component.getRowClass(tower)).toBe('urgency-red');
    });
  });

  describe('applyFilters()', () => {
    beforeEach(() => {
      apiSpy.getTowers.and.returnValue(of({ towers: mockTowers, count: 3 }));
      createComponent();
      fixture.detectChanges();
    });

    it('should show all towers when no filter is set', () => {
      component.providerFilter = '';
      component.regionFilter = '';
      component.towerTypeFilter = '';
      component.applyFilters();
      expect(component.filteredTowers.length).toBe(3);
    });

    it('should filter by provider using exact backend enum string', () => {
      component.providerFilter = 'crown_castle';
      component.applyFilters();
      expect(component.filteredTowers.length).toBe(1);
      expect(component.filteredTowers[0].provider).toBe('crown_castle');
    });

    it('should filter by region using exact backend enum string', () => {
      component.regionFilter = 'southeast';
      component.applyFilters();
      expect(component.filteredTowers.length).toBe(1);
      expect(component.filteredTowers[0].region).toBe('southeast');
    });

    it('should filter by tower_type using exact backend enum string', () => {
      component.towerTypeFilter = 'water_tower';
      component.applyFilters();
      expect(component.filteredTowers.length).toBe(1);
      expect(component.filteredTowers[0].tower_type).toBe('water_tower');
    });

    it('should apply multiple filters simultaneously', () => {
      component.providerFilter = 'sba_communications';
      component.regionFilter = 'southeast';
      component.towerTypeFilter = 'ground_mount';
      component.applyFilters();
      expect(component.filteredTowers.length).toBe(1);
      expect(component.filteredTowers[0].tower_id).toBe('ATT-FL-4205');
    });

    it('should return empty when filters match nothing', () => {
      component.providerFilter = 'crown_castle';
      component.regionFilter = 'west';
      component.applyFilters();
      expect(component.filteredTowers.length).toBe(0);
    });
  });

  describe('onNegotiate()', () => {
    it('should navigate to /towers/:tower_id using the tower_id from the backend response', () => {
      apiSpy.getTowers.and.returnValue(of({ towers: mockTowers, count: 3 }));
      createComponent();
      fixture.detectChanges();

      component.onNegotiate(mockTowers[0]);
      expect(router.navigate).toHaveBeenCalledWith(['/towers', 'ATT-NY-1201']);
    });

    it('should navigate using the correct tower_id for any tower', () => {
      apiSpy.getTowers.and.returnValue(of({ towers: mockTowers, count: 3 }));
      createComponent();
      fixture.detectChanges();

      component.onNegotiate(mockTowers[1]);
      expect(router.navigate).toHaveBeenCalledWith(['/towers', 'ATT-FL-4205']);
    });
  });
});
