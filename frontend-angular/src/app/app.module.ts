import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BrowserModule } from '@angular/platform-browser';

import { AccesoComponent } from './acceso/acceso.component';
import { AlertasComponent } from './alertas/alertas.component';
import { AnotacionesComponent } from './anotaciones/anotaciones.component';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { TokenInterceptor } from './core/token.interceptor';
import { LecturasComponent } from './lecturas/lecturas.component';

@NgModule({
  declarations: [AppComponent, AccesoComponent, LecturasComponent, AlertasComponent, AnotacionesComponent],
  imports: [BrowserModule, FormsModule, HttpClientModule, AppRoutingModule],
  providers: [{ provide: HTTP_INTERCEPTORS, useClass: TokenInterceptor, multi: true }],
  bootstrap: [AppComponent]
})
export class AppModule {}
