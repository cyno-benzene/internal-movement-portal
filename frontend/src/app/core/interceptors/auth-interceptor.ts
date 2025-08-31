import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthService } from '../services/auth';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(private authService: AuthService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = this.authService.getToken();
    
    // Add auth header if token exists
    let authReq = req;
    if (token) {
      authReq = req.clone({
        headers: req.headers.set('Authorization', `Bearer ${token}`)
      });
    }
    
    return next.handle(authReq).pipe(
      catchError((error: HttpErrorResponse) => {
        // Handle 401 Unauthorized errors
        if (error.status === 401) {
          // Check if the error is due to expired token
          if (error.error?.detail?.includes('expired') || 
              error.error?.detail?.includes('Could not validate credentials')) {
            this.authService.forceLogoutDueToExpiration();
          }
        }
        
        return throwError(() => error);
      })
    );
  }
}
