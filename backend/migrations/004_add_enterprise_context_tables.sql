-- Migration: Add Enterprise Context tables for organizational knowledge layer
-- This migration adds support for storing and managing enterprise context files
-- that provide organizational guidelines for AI agents.

-- ═══════════════════════════════════════════════════════════════════════════════
-- ENTERPRISE CONTEXTS TABLE (stores uploaded context files)
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS enterprise_contexts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    name TEXT NOT NULL,
    context_type TEXT NOT NULL CHECK (context_type IN ('company', 'division', 'team')),
    parent_id UUID REFERENCES enterprise_contexts(id) ON DELETE SET NULL,
    raw_content TEXT NOT NULL,
    parsed_content JSONB NOT NULL,
    validation_status TEXT DEFAULT 'pending' CHECK (validation_status IN ('pending', 'valid', 'invalid')),
    validation_errors JSONB DEFAULT '[]'::jsonb,
    scope TEXT DEFAULT 'private' CHECK (scope IN ('private', 'shared', 'organization')),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_ec_user ON enterprise_contexts(user_id);
CREATE INDEX IF NOT EXISTS idx_ec_type ON enterprise_contexts(context_type);
CREATE INDEX IF NOT EXISTS idx_ec_parent ON enterprise_contexts(parent_id);
CREATE INDEX IF NOT EXISTS idx_ec_scope ON enterprise_contexts(scope);
CREATE INDEX IF NOT EXISTS idx_ec_default ON enterprise_contexts(is_default) WHERE is_default = TRUE;

-- ═══════════════════════════════════════════════════════════════════════════════
-- SESSION-CONTEXT ASSOCIATION TABLE
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS session_contexts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL REFERENCES discovery_sessions(id) ON DELETE CASCADE,
    context_id UUID NOT NULL REFERENCES enterprise_contexts(id) ON DELETE CASCADE,
    context_type TEXT NOT NULL CHECK (context_type IN ('company', 'division', 'team')),
    merged_context JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(session_id, context_id)
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_sc_session ON session_contexts(session_id);
CREATE INDEX IF NOT EXISTS idx_sc_context ON session_contexts(context_id);

-- ═══════════════════════════════════════════════════════════════════════════════
-- ROW LEVEL SECURITY
-- ═══════════════════════════════════════════════════════════════════════════════

ALTER TABLE enterprise_contexts ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_contexts ENABLE ROW LEVEL SECURITY;

-- Enterprise contexts policies
CREATE POLICY "Service role can manage enterprise_contexts" ON enterprise_contexts
    FOR ALL USING (true) WITH CHECK (true);

-- Users can view their own contexts and organization-shared contexts
CREATE POLICY "Users can view own and shared contexts" ON enterprise_contexts
    FOR SELECT USING (
        user_id = auth.uid()
        OR scope = 'organization'
    );

-- Users can only modify their own contexts
CREATE POLICY "Users can modify own contexts" ON enterprise_contexts
    FOR ALL USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- Session contexts policies
CREATE POLICY "Service role can manage session_contexts" ON session_contexts
    FOR ALL USING (true) WITH CHECK (true);

-- ═══════════════════════════════════════════════════════════════════════════════
-- GRANTS
-- ═══════════════════════════════════════════════════════════════════════════════

GRANT ALL ON enterprise_contexts TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON enterprise_contexts TO authenticated;
GRANT ALL ON session_contexts TO service_role;
GRANT SELECT, INSERT, DELETE ON session_contexts TO authenticated;

-- ═══════════════════════════════════════════════════════════════════════════════
-- FUNCTION TO UPDATE updated_at TIMESTAMP
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION update_enterprise_context_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for auto-updating updated_at
DROP TRIGGER IF EXISTS enterprise_contexts_updated_at ON enterprise_contexts;
CREATE TRIGGER enterprise_contexts_updated_at
    BEFORE UPDATE ON enterprise_contexts
    FOR EACH ROW
    EXECUTE FUNCTION update_enterprise_context_updated_at();
