import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { TowerListComponent } from './pages/tower-list/tower-list.component';
import { TowerDetailComponent } from './pages/tower-detail/tower-detail.component';
import { NegotiationBriefComponent } from './pages/negotiation-brief/negotiation-brief.component';
import { TowerMapComponent } from './pages/tower-map/tower-map.component';
import { BenchmarksComponent } from './pages/benchmarks/benchmarks.component';
import { UtilizationComponent } from './pages/utilization/utilization.component';
import { ComparablesComponent } from './pages/comparables/comparables.component';
import { RegulatoryComponent } from './pages/regulatory/regulatory.component';
import { TimelineComponent } from './pages/timeline/timeline.component';

const routes: Routes = [
  { path: 'towers', component: TowerListComponent },
  { path: 'towers/:id', component: TowerDetailComponent },
  { path: 'brief/:session', component: NegotiationBriefComponent },
  { path: 'map', component: TowerMapComponent },
  { path: 'benchmarks', component: BenchmarksComponent },
  { path: 'utilization', component: UtilizationComponent },
  { path: 'comparables', component: ComparablesComponent },
  { path: 'regulatory', component: RegulatoryComponent },
  { path: 'timeline', component: TimelineComponent },
  { path: '', redirectTo: '/towers', pathMatch: 'full' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
