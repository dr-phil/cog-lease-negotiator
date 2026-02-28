import { Component } from '@angular/core';
import { REGULATORY_MATRIX, REGIONS, TOWER_TYPES, RegulatoryCell } from '../../data/regulatory-data';

@Component({
  selector: 'app-regulatory',
  templateUrl: './regulatory.component.html',
  styleUrls: ['./regulatory.component.scss'],
})
export class RegulatoryComponent {
  regions = REGIONS;
  towerTypes = TOWER_TYPES;
  matrix = REGULATORY_MATRIX;

  expandedCell: { region: string; towerType: string } | null = null;

  getCell(region: string, towerType: string): RegulatoryCell {
    return this.matrix[region][towerType];
  }

  getRiskClass(level: string): string {
    switch (level) {
      case 'elevated': return 'risk-elevated';
      case 'moderate': return 'risk-moderate';
      default: return 'risk-low';
    }
  }

  toggleCell(region: string, towerType: string): void {
    if (this.expandedCell?.region === region && this.expandedCell?.towerType === towerType) {
      this.expandedCell = null;
    } else {
      this.expandedCell = { region, towerType };
    }
  }

  isExpanded(region: string, towerType: string): boolean {
    return this.expandedCell?.region === region && this.expandedCell?.towerType === towerType;
  }

  formatLabel(value: string): string {
    return value.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  }
}
