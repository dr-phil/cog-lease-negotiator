import { Component, OnInit } from '@angular/core';
import { TOWER_INVENTORY } from '../../data/tower-inventory';
import { TowerInfo } from '../../models/tower-lease.models';

interface TimelineTower extends TowerInfo {
  expiryDate: Date;
  isUrgent: boolean;
  barLeft: number;
  barWidth: number;
}

interface ProviderGroup {
  provider: string;
  label: string;
  towers: TimelineTower[];
}

@Component({
  selector: 'app-timeline',
  templateUrl: './timeline.component.html',
  styleUrls: ['./timeline.component.scss'],
})
export class TimelineComponent implements OnInit {
  providerGroups: ProviderGroup[] = [];
  timelineMonths: { label: string; position: number }[] = [];

  private timelineStart!: Date;
  private timelineEnd!: Date;
  private totalMs!: number;

  ngOnInit(): void {
    const now = new Date();
    const sixMonthsFromNow = new Date(now);
    sixMonthsFromNow.setMonth(sixMonthsFromNow.getMonth() + 6);

    // Timeline range: 2025-01-01 to 2027-01-01
    this.timelineStart = new Date('2025-01-01');
    this.timelineEnd = new Date('2027-01-01');
    this.totalMs = this.timelineEnd.getTime() - this.timelineStart.getTime();

    const providerOrder = ['crown_castle', 'american_tower', 'sba_communications', 'municipal', 'rural_individual'];
    const providerLabels: Record<string, string> = {
      crown_castle: 'Crown Castle',
      american_tower: 'American Tower',
      sba_communications: 'SBA Communications',
      municipal: 'Municipal',
      rural_individual: 'Rural Individual',
    };

    const grouped: Record<string, TimelineTower[]> = {};

    TOWER_INVENTORY.forEach((tower) => {
      const expiryDate = new Date(tower.lease_expiry);
      const isUrgent = expiryDate.getTime() <= sixMonthsFromNow.getTime() && expiryDate.getTime() >= now.getTime();

      // Bar: from timeline start to expiry
      const barLeft = 0;
      const expiryMs = expiryDate.getTime() - this.timelineStart.getTime();
      const barWidth = Math.max(0, Math.min(100, (expiryMs / this.totalMs) * 100));

      const tlTower: TimelineTower = {
        ...tower,
        expiryDate,
        isUrgent,
        barLeft,
        barWidth,
      };

      if (!grouped[tower.provider]) {
        grouped[tower.provider] = [];
      }
      grouped[tower.provider].push(tlTower);
    });

    this.providerGroups = providerOrder
      .filter((p) => grouped[p]?.length)
      .map((p) => ({
        provider: p,
        label: providerLabels[p] || p,
        towers: grouped[p].sort((a, b) => a.expiryDate.getTime() - b.expiryDate.getTime()),
      }));

    // Generate month labels
    this.timelineMonths = [];
    const cursor = new Date(this.timelineStart);
    while (cursor <= this.timelineEnd) {
      const pos = ((cursor.getTime() - this.timelineStart.getTime()) / this.totalMs) * 100;
      const label = cursor.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
      this.timelineMonths.push({ label, position: pos });
      cursor.setMonth(cursor.getMonth() + 3);
    }
  }

  getNowPosition(): number {
    const now = new Date();
    return ((now.getTime() - this.timelineStart.getTime()) / this.totalMs) * 100;
  }
}
