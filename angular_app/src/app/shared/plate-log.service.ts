import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PlateLogs } from './Plate_logs';

@Injectable({
  providedIn: 'root'
})
export class PlateLogService {
  private apiUrl = 'http://localhost:5000/api/plate_logs';

  constructor(private http: HttpClient) { }

  getPlateLogs(): Observable<PlateLogs[]> {
    return this.http.get<PlateLogs[]>(this.apiUrl);
  }

  addPlateLogs(plateLogs: PlateLogs[]): Observable<any> {
    return this.http.post<any>(this.apiUrl, plateLogs);
  }

  clearPlateLogs(): Observable<any> {
    return this.http.delete<any>(this.apiUrl);
  }
}
