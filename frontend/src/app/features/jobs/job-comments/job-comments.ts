import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ApiService } from '../../../core/services/api';
import { AuthService } from '../../../core/services/auth';
import { JobComment, JobCommentCreate } from '../../../core/models/job-comment.model';

@Component({
  selector: 'app-job-comments',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatSnackBarModule,
    MatTooltipModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './job-comments.html',
  styleUrl: './job-comments.scss'
})
export class JobCommentsComponent implements OnInit {
  @Input() jobId!: string;
  
  comments: JobComment[] = [];
  commentForm: FormGroup;
  isLoading = false;
  isSubmitting = false;
  currentUser: any;

  constructor(
    private fb: FormBuilder,
    private apiService: ApiService,
    private authService: AuthService,
    private snackBar: MatSnackBar
  ) {
    this.commentForm = this.fb.group({
      content: ['', [Validators.required, Validators.minLength(5)]]
    });
  }

  ngOnInit(): void {
    this.currentUser = this.authService.getCurrentUser();
    this.loadComments();
  }

  loadComments(): void {
    if (!this.jobId) return;
    
    this.isLoading = true;
    this.apiService.getJobComments(this.jobId).subscribe({
      next: (comments) => {
        this.comments = comments;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading comments:', error);
        this.isLoading = false;
        this.snackBar.open('Failed to load comments', 'Close', { duration: 3000 });
      }
    });
  }

  onSubmit(): void {
    if (this.commentForm.valid && !this.isSubmitting) {
      this.isSubmitting = true;
      
      const content = this.commentForm.value.content;

      this.apiService.createJobComment(this.jobId, content).subscribe({
        next: (newComment) => {
          this.comments.push(newComment);
          this.commentForm.reset();
          this.isSubmitting = false;
          this.snackBar.open('Comment added successfully', 'Close', { duration: 3000 });
        },
        error: (error) => {
          console.error('Error creating comment:', error);
          this.isSubmitting = false;
          this.snackBar.open('Failed to add comment', 'Close', { duration: 3000 });
        }
      });
    }
  }

  canComment(): boolean {
    return this.currentUser && ['manager', 'hr', 'admin'].includes(this.currentUser.role);
  }

  getRoleDisplayName(role: string): string {
    const roleMap: { [key: string]: string } = {
      'manager': 'Manager',
      'hr': 'HR',
      'admin': 'Admin',
      'employee': 'Employee'
    };
    return roleMap[role] || role;
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleString();
  }
}
