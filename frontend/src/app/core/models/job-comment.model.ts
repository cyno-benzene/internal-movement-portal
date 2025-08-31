export interface JobComment {
  id: string;
  job_id: string;
  author_id: string;
  author_name: string;
  author_role: string;
  content: string;
  created_at: string;
}

export interface JobCommentCreate {
  content: string;
}
