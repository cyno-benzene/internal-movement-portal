-- Add job_comments table for job discussions between managers and HR
-- Migration: add_job_comments_table

CREATE TABLE job_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for performance
CREATE INDEX idx_job_comments_job_id ON job_comments(job_id);
CREATE INDEX idx_job_comments_author_id ON job_comments(author_id);
CREATE INDEX idx_job_comments_created_at ON job_comments(created_at);

-- Add a comment explaining the table purpose
COMMENT ON TABLE job_comments IS 'Comments on job postings for communication between managers and HR';
