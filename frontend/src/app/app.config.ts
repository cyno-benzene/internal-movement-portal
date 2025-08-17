import { ApplicationConfig, provideBrowserGlobalErrorListeners, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideAnimations } from '@angular/platform-browser/animations';
import { routes } from './app.routes';
import { AuthInterceptor } from './core/interceptors/auth-interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideHttpClient(
      withInterceptors([
        (req, next) => {
          const authService = new (AuthInterceptor as any)();
          // This is a functional interceptor approach for Angular 17+
          const token = localStorage.getItem('access_token');
          console.log('Functional Interceptor - URL:', req.url);
          console.log('Functional Interceptor - Token exists:', !!token);
          
          if (token) {
            console.log('Functional Interceptor - Adding Authorization header');
            const authReq = req.clone({
              headers: req.headers.set('Authorization', `Bearer ${token}`)
            });
            return next(authReq);
          }
          
          console.log('Functional Interceptor - No token, proceeding without auth header');
          return next(req);
        }
      ])
    ),
    provideAnimations()
  ]
};
