import { Injectable, OnDestroy } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap, timer, Subscription } from 'rxjs';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { environment } from '../../../environments/environment';
import { User, LoginRequest, TokenResponse } from '../models/user.model';

interface DecodedToken {
  exp: number;
  sub: string;
  employee_id: string;
  role: string;
  email: string;
  name: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService implements OnDestroy {
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();
  
  private sessionTimerSubscription?: Subscription;
  private expirationTimerSubscription?: Subscription;
  private warningShown = false;
  private readonly SESSION_WARNING_MINUTES = 0.17;
  constructor(
    private http: HttpClient,
    private router: Router,
    private snackBar: MatSnackBar
  ) {
    this.loadUserFromStorage();
    this.startSessionMonitoring();
  }

  login(credentials: LoginRequest): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${environment.apiUrl}/auth/login`, credentials)
      .pipe(
        tap(response => {
          localStorage.setItem('access_token', response.access_token);
          
          // Decode and log token info for debugging
          const tokenData = this.decodeToken(response.access_token);
          if (tokenData) {
            const expirationTime = new Date(tokenData.exp * 1000);
          }
          
          const user: User = {
            id: response.user_id,
            employee_id: response.employee_id,
            email: response.email,
            name: response.name,
            role: response.role as any
          };
          localStorage.setItem('current_user', JSON.stringify(user));
          this.currentUserSubject.next(user);
          this.warningShown = false;
          this.startSessionMonitoring();
        })
      );
  }

  logout(showMessage: boolean = true): void {
    if (this.sessionTimerSubscription) {
      this.sessionTimerSubscription.unsubscribe();
    }
    if (this.expirationTimerSubscription) {
      this.expirationTimerSubscription.unsubscribe();
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('current_user');
    this.currentUserSubject.next(null);
    this.warningShown = false;
    
    if (showMessage) {
      this.snackBar.open('You have been logged out', 'Close', {
        duration: 3000,
        panelClass: ['info-snackbar']
      });
    }
    
    this.router.navigate(['/login']);
  }

  forceLogoutDueToExpiration(): void {
    if (this.sessionTimerSubscription) {
      this.sessionTimerSubscription.unsubscribe();
    }
    if (this.expirationTimerSubscription) {
      this.expirationTimerSubscription.unsubscribe();
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('current_user');
    this.currentUserSubject.next(null);
    this.warningShown = false;
    
    this.snackBar.open('Your session has expired. Please log in again.', 'Close', {
      duration: 5000,
      panelClass: ['error-snackbar']
    });
    
    this.router.navigate(['/login']);
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  isAuthenticated(): boolean {
    const token = this.getToken();
    if (!token || !this.getCurrentUser()) {
      return false;
    }
    
    // Check if token is expired
    const tokenData = this.decodeToken(token);
    if (!tokenData || this.isTokenExpired(tokenData)) {
      this.forceLogoutDueToExpiration();
      return false;
    }
    
    return true;
  }

  hasRole(roles: string[]): boolean {
    const user = this.getCurrentUser();
    return user ? roles.includes(user.role) : false;
  }

  getTokenExpirationTime(): Date | null {
    const token = this.getToken();
    if (!token) return null;
    
    const decoded = this.decodeToken(token);
    return decoded ? new Date(decoded.exp * 1000) : null;
  }

  getTimeUntilExpiration(): number {
    const expirationTime = this.getTokenExpirationTime();
    if (!expirationTime) return 0;
    
    return Math.max(0, expirationTime.getTime() - Date.now());
  }

  private decodeToken(token: string): DecodedToken | null {
    try {
      const payload = token.split('.')[1];
      const decoded = JSON.parse(atob(payload));
      return decoded;
    } catch (error) {
      console.error('Error decoding token:', error);
      return null;
    }
  }

  private isTokenExpired(tokenData: DecodedToken): boolean {
    const currentTime = Math.floor(Date.now() / 1000);
    return tokenData.exp < currentTime;
  }

  private startSessionMonitoring(): void {
    console.log('🔄 Starting session monitoring...');
    
    // Clear any existing timers
    if (this.sessionTimerSubscription) {
      this.sessionTimerSubscription.unsubscribe();
      console.log('🗑️ Cleared existing warning timer');
    }
    if (this.expirationTimerSubscription) {
      this.expirationTimerSubscription.unsubscribe();
      console.log('🗑️ Cleared existing expiration timer');
    }

    const token = this.getToken();
    if (!token) {
      console.log('❌ No token found for monitoring');
      return;
    }

    const decoded = this.decodeToken(token);
    if (!decoded) {
      console.log('❌ Could not decode token for monitoring');
      return;
    }

    console.log('🔍 Token decoded for monitoring:', {
      exp: decoded.exp,
      expiration_date: new Date(decoded.exp * 1000),
      current_time: new Date()
    });

    const expirationTime = decoded.exp * 1000;
    const currentTime = Date.now();
    const timeUntilExpiration = expirationTime - currentTime;
    const warningTime = timeUntilExpiration - (this.SESSION_WARNING_MINUTES * 60 * 1000);

    console.log('📊 Session timing:', {
      timeUntilExpiration: Math.floor(timeUntilExpiration / 1000) + ' seconds',
      warningTime: Math.floor(warningTime / 1000) + ' seconds'
    });

    // If token expires soon, show warning immediately
    if (warningTime <= 0 && timeUntilExpiration > 0) {
      console.log('⚠️ Token expires very soon, showing warning immediately');
      this.showSessionWarning();
    } else if (warningTime > 0) {
      // Set timer for warning
      console.log('⏰ Setting warning timer for', Math.floor(warningTime / 1000), 'seconds');
      this.sessionTimerSubscription = timer(warningTime).subscribe(() => {
        console.log('⚠️ Warning timer triggered');
        this.showSessionWarning();
      });
    }

    // Set timer for automatic logout on expiration
    if (timeUntilExpiration > 0) {
      console.log('⏰ Setting expiration timer for', Math.floor(timeUntilExpiration / 1000), 'seconds');
      this.expirationTimerSubscription = timer(timeUntilExpiration).subscribe(() => {
        console.log('💀 Expiration timer triggered, forcing logout');
        this.forceLogoutDueToExpiration();
      });
    } else {
      console.log('💀 Token already expired, forcing logout immediately');
      this.forceLogoutDueToExpiration();
    }
  }

  private showSessionWarning(): void {
    if (this.warningShown) {
      return;
    }
    
    this.warningShown = true;
    const timeLeft = Math.ceil(this.getTimeUntilExpiration() / (60 * 1000));
    
    const snackBarRef = this.snackBar.open(
      `Your session will expire in ${timeLeft} minute(s). Click to extend session.`,
      'Extend Session',
      {
        duration: 0, // Don't auto-dismiss
        panelClass: ['warning-snackbar']
      }
    );

    snackBarRef.onAction().subscribe(() => {
      this.refreshSession();
    });

    // Auto-dismiss after 30 seconds if no action
    timer(30000).subscribe(() => {
      snackBarRef.dismiss();
    });
  }

  private refreshSession(): void {
    console.log('🔄 Attempting to refresh session...');
    const currentToken = this.getToken();
    console.log('🔑 Current token for refresh:', currentToken ? 'EXISTS' : 'MISSING');
    
    // Call the refresh token endpoint to get a new token
    this.http.post(`${environment.apiUrl}/auth/refresh`, {}).subscribe({
      next: (response: any) => {
        console.log('✅ Session refresh successful, new token received');
        console.log('🔑 New token exp:', this.decodeToken(response.access_token)?.exp);
        console.log('🔑 Old token exp:', this.decodeToken(currentToken!)?.exp);
        
        // Store the new token using the same key as login
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('current_user', JSON.stringify({
          id: response.user_id,
          employee_id: response.employee_id,
          email: response.email,
          role: response.role,
          name: response.name
        }));
        
        // Verify token was stored
        const storedToken = this.getToken();
        console.log('🔑 Token stored correctly:', storedToken === response.access_token);
        console.log('🔑 New stored token exp:', this.decodeToken(storedToken!)?.exp);
        
        this.warningShown = false;
        this.snackBar.open('Session extended successfully', 'Close', {
          duration: 3000,
          panelClass: ['success-snackbar']
        });
        
        // Restart monitoring with the new token
        console.log('🔄 Restarting session monitoring with new token...');
        this.startSessionMonitoring();
      },
      error: (error) => {
        this.forceLogoutDueToExpiration();
      }
    });
  }

  private loadUserFromStorage(): void {
    const userStr = localStorage.getItem('current_user');
    if (userStr) {
      const user = JSON.parse(userStr);
      this.currentUserSubject.next(user);
      
      // Check if current token is still valid
      if (this.isAuthenticated()) {
        this.startSessionMonitoring();
      }
    }
  }

  ngOnDestroy(): void {
    if (this.sessionTimerSubscription) {
      this.sessionTimerSubscription.unsubscribe();
    }
    if (this.expirationTimerSubscription) {
      this.expirationTimerSubscription.unsubscribe();
    }
  }
}
