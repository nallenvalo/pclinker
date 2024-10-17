import { Injectable, NgModule } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import {checkLogs} from './checkLogs'

@Injectable({
  providedIn: 'root'
})

@NgModule({
  exports : [CheckConnectionService]
})

export class CheckConnectionService {
  //private apiUrl = 'http://localhost:5000/api/check_logs';

  constructor(private http: HttpClient) { }

  // recieveConnectionCheck(): Observable<checkLogs[]> {
  //   return this.http.get<checkLogs[]>(this.apiUrl);
  // }

  // sendConnectionCheck(plateLogs: checkLogs[]): Observable<any> {
  //   return this.http.post<any>(this.apiUrl, plateLogs);
  // }
}
