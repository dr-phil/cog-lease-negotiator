import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import {
  NegotiateRequest,
  NegotiateResponse,
  FollowupRequest,
  FollowupResponse,
  TowerInfo,
} from '../models/tower-lease.models';

@Injectable({ providedIn: 'root' })
export class TowerLeaseApiService {
  private base = environment.apiBase;

  constructor(private http: HttpClient) {}

  getTowers(): Observable<{ towers: TowerInfo[]; count: number }> {
    return this.http.get<{ towers: TowerInfo[]; count: number }>(
      `${this.base}/api/towers`
    );
  }

  negotiate(req: NegotiateRequest): Observable<NegotiateResponse> {
    return this.http.post<NegotiateResponse>(
      `${this.base}/api/negotiate`,
      req
    );
  }

  followup(req: FollowupRequest): Observable<FollowupResponse> {
    return this.http.post<FollowupResponse>(
      `${this.base}/api/followup`,
      req
    );
  }
}
