-- Migration: Add run_memories table for cross-run learning
-- Requires pgvector extension (available in Supabase)

-- Enable pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Create run_memories table for storing high-quality agent outputs
CREATE TABLE IF NOT EXISTS run_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    session_id TEXT REFERENCES discovery_sessions(id) ON DELETE SET NULL,
    domain_type TEXT NOT NULL,
    industry TEXT,
    agent_name TEXT NOT NULL,
    quality_score FLOAT NOT NULL,
    content_summary TEXT NOT NULL,
    -- text-embedding-004 produces 768-dimensional embeddings
    embedding VECTOR(768),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Only store high-quality outputs (threshold enforced at application level)
    CONSTRAINT quality_threshold CHECK (quality_score >= 0.7)
);

-- Index for filtering by domain type
CREATE INDEX IF NOT EXISTS idx_memories_domain ON run_memories(domain_type);

-- Index for filtering by agent name
CREATE INDEX IF NOT EXISTS idx_memories_agent ON run_memories(agent_name);

-- Index for filtering by user
CREATE INDEX IF NOT EXISTS idx_memories_user ON run_memories(user_id);

-- Index for vector similarity search using cosine distance
-- Using ivfflat for approximate nearest neighbor search
CREATE INDEX IF NOT EXISTS idx_memories_embedding ON run_memories
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Function to match similar memories
CREATE OR REPLACE FUNCTION match_memories(
    query_embedding VECTOR(768),
    match_threshold FLOAT,
    match_count INT,
    filter_domain TEXT DEFAULT NULL,
    filter_agent TEXT DEFAULT NULL,
    filter_user_id UUID DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    domain_type TEXT,
    agent_name TEXT,
    quality_score FLOAT,
    content_summary TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        rm.id,
        rm.domain_type,
        rm.agent_name,
        rm.quality_score,
        rm.content_summary,
        1 - (rm.embedding <=> query_embedding) AS similarity
    FROM run_memories rm
    WHERE
        (filter_domain IS NULL OR rm.domain_type = filter_domain)
        AND (filter_agent IS NULL OR rm.agent_name = filter_agent)
        AND (filter_user_id IS NULL OR rm.user_id = filter_user_id)
        AND 1 - (rm.embedding <=> query_embedding) > match_threshold
    ORDER BY rm.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Grant permissions (adjust as needed for your Supabase setup)
GRANT SELECT ON run_memories TO authenticated;
GRANT INSERT ON run_memories TO authenticated;
GRANT EXECUTE ON FUNCTION match_memories TO authenticated;

-- Add RLS policy for user isolation
ALTER TABLE run_memories ENABLE ROW LEVEL SECURITY;

-- Users can only see their own memories
CREATE POLICY "Users can view own memories"
    ON run_memories FOR SELECT
    USING (auth.uid() = user_id);

-- Users can only insert their own memories
CREATE POLICY "Users can insert own memories"
    ON run_memories FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Optional: Allow viewing of anonymized high-quality examples (for learning across users)
-- CREATE POLICY "Users can view high quality examples"
--     ON run_memories FOR SELECT
--     USING (quality_score >= 0.9);
