import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { provideHttpClient, withFetch} from '@angular/common/http';  // Import provideHttpClient

import { AppComponent } from './app.component';

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    BrowserModule,
  ],
  providers: [provideHttpClient(withFetch())],  // Provide HttpClient here
  bootstrap: [AppComponent]
})
export class AppModule { }
