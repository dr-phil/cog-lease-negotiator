import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { TowerListComponent } from './pages/tower-list/tower-list.component';
import { TowerDetailComponent } from './pages/tower-detail/tower-detail.component';
import { NegotiationBriefComponent } from './pages/negotiation-brief/negotiation-brief.component';
import { TowerMapComponent } from './pages/tower-map/tower-map.component';
import { BenchmarksComponent } from './pages/benchmarks/benchmarks.component';
import { BenchmarkRatePipe } from './pages/benchmarks/benchmark-rate.pipe';
import { UtilizationComponent } from './pages/utilization/utilization.component';
import { ComparablesComponent } from './pages/comparables/comparables.component';
import { RegulatoryComponent } from './pages/regulatory/regulatory.component';
import { TimelineComponent } from './pages/timeline/timeline.component';

@NgModule({
  declarations: [
    AppComponent,
    TowerListComponent,
    TowerDetailComponent,
    NegotiationBriefComponent,
    TowerMapComponent,
    BenchmarksComponent,
    BenchmarkRatePipe,
    UtilizationComponent,
    ComparablesComponent,
    RegulatoryComponent,
    TimelineComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
  ],
  providers: [],
  bootstrap: [AppComponent],
})
export class AppModule {}
