-- Migration: Add Discovery V4 tables for hybrid discovery system
-- This migration adds support for the staged discovery process with
-- multiple modes (Quick, Guided, Deep)

-- Ensure additional_context column exists in discovery_sessions
-- (This column stores V4 session state as JSON)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'discovery_sessions'
        AND column_name = 'additional_context'
    ) THEN
        ALTER TABLE discovery_sessions ADD COLUMN additional_context TEXT;
    END IF;
END $$;

-- Create draft_states table for storing stage outputs
CREATE TABLE IF NOT EXISTS draft_states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL REFERENCES discovery_sessions(id) ON DELETE CASCADE,
    stage_name TEXT NOT NULL,
    stage_output JSONB,
    stage_status TEXT DEFAULT 'pending',
    user_edits JSONB DEFAULT '[]'::jsonb,
    ai_coaching JSONB DEFAULT '[]'::jsonb,
    score INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(session_id, stage_name)
);

-- Create index for faster lookups by session
CREATE INDEX IF NOT EXISTS idx_draft_states_session ON draft_states(session_id);

-- Create interviews table for customer interview data
CREATE TABLE IF NOT EXISTS interviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL REFERENCES discovery_sessions(id) ON DELETE CASCADE,
    interviewee_name TEXT,
    interviewee_role TEXT,
    company_type TEXT,
    company_size TEXT,
    interview_date DATE,
    story_raw TEXT,
    key_quote TEXT,
    struggling_moment TEXT,
    emotions TEXT[],
    current_workaround TEXT,
    desired_outcome TEXT,
    ai_extracted_insights JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for faster lookups by session
CREATE INDEX IF NOT EXISTS idx_interviews_session ON interviews(session_id);

-- Create pattern_synthesis table for interview pattern analysis
CREATE TABLE IF NOT EXISTS pattern_synthesis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL REFERENCES discovery_sessions(id) ON DELETE CASCADE,
    pain_patterns JSONB DEFAULT '[]'::jsonb,
    trigger_patterns JSONB DEFAULT '[]'::jsonb,
    outcome_patterns JSONB DEFAULT '[]'::jsonb,
    contradictions JSONB DEFAULT '[]'::jsonb,
    interview_gaps JSONB DEFAULT '[]'::jsonb,
    synthesized_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(session_id)
);

-- Enable RLS on new tables
ALTER TABLE draft_states ENABLE ROW LEVEL SECURITY;
ALTER TABLE interviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE pattern_synthesis ENABLE ROW LEVEL SECURITY;

-- Create policies for draft_states
CREATE POLICY "Service role can manage draft_states" ON draft_states
    FOR ALL USING (true) WITH CHECK (true);

-- Create policies for interviews
CREATE POLICY "Service role can manage interviews" ON interviews
    FOR ALL USING (true) WITH CHECK (true);

-- Create policies for pattern_synthesis
CREATE POLICY "Service role can manage pattern_synthesis" ON pattern_synthesis
    FOR ALL USING (true) WITH CHECK (true);

-- Grant permissions
GRANT ALL ON draft_states TO service_role;
GRANT ALL ON interviews TO service_role;
GRANT ALL ON pattern_synthesis TO service_role;
