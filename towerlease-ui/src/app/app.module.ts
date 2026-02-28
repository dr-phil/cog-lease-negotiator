import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { TowerListComponent } from './pages/tower-list/tower-list.component';
import { TowerDetailComponent } from './pages/tower-detail/tower-detail.component';
import { NegotiationBriefComponent } from './pages/negotiation-brief/negotiation-brief.component';

@NgModule({
  declarations: [
    AppComponent,
    TowerListComponent,
    TowerDetailComponent,
    NegotiationBriefComponent,
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
