import { Component, OnInit, OnDestroy, ElementRef, ViewChild, AfterViewInit } from '@angular/core';
import * as L from 'leaflet';
import { TOWER_INVENTORY } from '../../data/tower-inventory';
import { TowerInfo } from '../../models/tower-lease.models';

@Component({
  selector: 'app-tower-map',
  templateUrl: './tower-map.component.html',
  styleUrls: ['./tower-map.component.scss'],
})
export class TowerMapComponent implements AfterViewInit, OnDestroy {
  @ViewChild('mapContainer', { static: true }) mapContainer!: ElementRef;

  towers = TOWER_INVENTORY;
  selectedTower: TowerInfo | null = null;
  private map!: L.Map;
  private markers: L.Marker[] = [];

  ngAfterViewInit(): void {
    this.initMap();
  }

  ngOnDestroy(): void {
    if (this.map) {
      this.map.remove();
    }
  }

  private initMap(): void {
    this.map = L.map(this.mapContainer.nativeElement).setView([39.0, -95.0], 4);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
    }).addTo(this.map);

    this.towers.forEach((tower) => {
      const color = this.getPinColor(tower.current_monthly_rate);
      const icon = L.divIcon({
        className: 'custom-marker',
        html: `<div style="
          width: 16px; height: 16px; border-radius: 50%;
          background-color: ${color}; border: 2px solid #fff;
          box-shadow: 0 2px 4px rgba(0,0,0,0.4);
        "></div>`,
        iconSize: [16, 16],
        iconAnchor: [8, 8],
      });

      const marker = L.marker([tower.coordinates.lat, tower.coordinates.lng], { icon })
        .addTo(this.map)
        .on('click', () => this.selectTower(tower));

      this.markers.push(marker);
    });
  }

  private getPinColor(rate: number): string {
    if (rate > 12000) return '#e53935';
    if (rate >= 5000) return '#fdd835';
    return '#43a047';
  }

  selectTower(tower: TowerInfo): void {
    this.selectedTower = tower;
  }

  closeSidebar(): void {
    this.selectedTower = null;
  }

  formatCurrency(value: number): string {
    return '$' + value.toLocaleString();
  }

  formatProvider(provider: string): string {
    return provider.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  }

  formatType(type: string): string {
    return type.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  }
}
