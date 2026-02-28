import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { TowerListComponent } from './pages/tower-list/tower-list.component';
import { TowerDetailComponent } from './pages/tower-detail/tower-detail.component';
import { NegotiationBriefComponent } from './pages/negotiation-brief/negotiation-brief.component';

const routes: Routes = [
  { path: 'towers', component: TowerListComponent },
  { path: 'towers/:id', component: TowerDetailComponent },
  { path: 'brief/:session', component: NegotiationBriefComponent },
  { path: '', redirectTo: '/towers', pathMatch: 'full' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
