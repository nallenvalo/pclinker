import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { provideHttpClient, withFetch} from '@angular/common/http';  // Import provideHttpClient
import { CheckConnectionComponent } from './check-connection/check-connection.component';
import { AppComponent } from './app.component';

@NgModule({
  declarations: [
    AppComponent, CheckConnectionComponent
  ],
  imports: [
    BrowserModule,
  ],
  providers: [provideHttpClient(withFetch())],  // Provide HttpClient here
  bootstrap: [AppComponent]
})
export class AppModule { }

