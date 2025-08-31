-- Add priority column to jobs table
-- Migration: add_job_priority_column

ALTER TABLE jobs 
ADD COLUMN priority VARCHAR(50) DEFAULT 'normal';

-- Add a comment explaining the priority values
COMMENT ON COLUMN jobs.priority IS 'Job priority: normal (default, not displayed) or high_importance (displayed with flag)';
