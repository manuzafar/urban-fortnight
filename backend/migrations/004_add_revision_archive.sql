-- Migration: Add revision_archive table for storing pruned revision history
-- This table stores old revision history entries that have been pruned from
-- active session state to reduce memory footprint.

-- Create revision_archive table for storing archived revision history
CREATE TABLE IF NOT EXISTS revision_archive (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL REFERENCES discovery_sessions(id) ON DELETE CASCADE,
    revision_index INTEGER NOT NULL,
    revision_data JSONB NOT NULL,
    archived_at TIMESTAMPTZ DEFAULT NOW(),

    -- Ensure we don't archive the same revision twice
    UNIQUE(session_id, revision_index)
);

-- Index for faster lookups by session
CREATE INDEX IF NOT EXISTS idx_revision_archive_session ON revision_archive(session_id);

-- Index for time-based queries (e.g., cleanup of old archives)
CREATE INDEX IF NOT EXISTS idx_revision_archive_time ON revision_archive(archived_at);

-- Enable RLS
ALTER TABLE revision_archive ENABLE ROW LEVEL SECURITY;

-- Create policy for service role access
CREATE POLICY "Service role can manage revision_archive" ON revision_archive
    FOR ALL USING (true) WITH CHECK (true);

-- Grant permissions to service role
GRANT ALL ON revision_archive TO service_role;

-- Optional: Create a function to clean up old archives
-- This can be called periodically to remove archives older than a retention period
CREATE OR REPLACE FUNCTION cleanup_old_revision_archives(
    retention_days INTEGER DEFAULT 30
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM revision_archive
    WHERE archived_at < NOW() - (retention_days || ' days')::INTERVAL;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    RETURN deleted_count;
END;
$$;

-- Grant execute permission on cleanup function
GRANT EXECUTE ON FUNCTION cleanup_old_revision_archives TO service_role;

-- Add comment for documentation
COMMENT ON TABLE revision_archive IS
'Stores pruned revision history entries from discovery sessions.
Old revisions are archived here when state pruning is performed to keep
active session state small while preserving historical data for debugging.';

COMMENT ON FUNCTION cleanup_old_revision_archives IS
'Removes revision archives older than the specified retention period (default 30 days).
Should be called periodically as a maintenance task.';
