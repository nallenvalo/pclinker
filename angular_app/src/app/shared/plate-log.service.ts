import { Injectable, NgModule } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { concatMap, Observable } from 'rxjs';
import { PlateLogs } from './Plate_logs';
import { checkLogs } from '../check-connection/checkLogs'
import { shortedHarvard } from '../config-table/shortedHarvard';
import { ConfigTable } from '../config-table/ConfigTable';
import { response } from 'express';

@Injectable({
  providedIn: 'root'
})

export class PlateLogService {
  private apiUrl = 'http://localhost:5000/api/plate_logs';
  private apiUrl2 = 'http://localhost:5000/api/check_logs';
  private apiUrlPC2 = 'http://10.10.100.56:5000/api/check_logs';

  private apiUrl3 = 'http://localhost:5000/api/shorted_harvard';
  private apiUrl3PC2 = 'http://10.10.100.56:5000/api/shorted_harvard';

  constructor(private http: HttpClient) { }
  // plate log linkers
  getPlateLogs(): Observable<PlateLogs[]> {
    return this.http.get<PlateLogs[]>(this.apiUrl);
  }

  addPlateLogs(plateLogs: PlateLogs[]): Observable<any> {
    return this.http.post<any>(this.apiUrl, plateLogs);
  }

  clearPlateLogs(): Observable<any> {
    return this.http.delete<any>(this.apiUrl);
  }

  // check table linkers
  recieveConnectionCheck(): Observable<checkLogs[]> {
    return this.http.get<checkLogs[]>(this.apiUrl2);
  }
  
  sendConnectionCheck(checkLogs: checkLogs[]): Observable<any> {
    return this.http.post<any>(this.apiUrl2, checkLogs).pipe(
      concatMap(response1 => {
        console.log('first request completed : ', response1);
        return this.http.post<any>(this.apiUrlPC2, checkLogs);
      })
    );
  }

  // config table linkers
  SendConfigTable(table : ConfigTable[]): Observable<any>{
    console.log('sending config table:', table)
    return this.http.post<any>(this.apiUrl3, table);

    // return this.http.post<any>(this.apiUrl3, table).pipe(
    //   concatMap(response1 => {
    //     console.log('first request completed : ', response1);
    //     return this.http.post<any>(this.apiUrl3PC2, table);
    //   })
    // );
  }

  RetrieveConfigTable(): Observable<any>{
    return this.http.get<ConfigTable[]>(this.apiUrl3);
  }

  RetrieveHarvardData(): Observable<any>{
    return this.http.get<shortedHarvard[]>(this.apiUrl3);
  }

}



