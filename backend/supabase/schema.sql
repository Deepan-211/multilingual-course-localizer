-- Supabase schema for Multilingual Content Localization Engine
-- Run this in the Supabase SQL Editor

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    avatar_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- User settings / preferences
CREATE TABLE IF NOT EXISTS user_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    default_source_language TEXT NOT NULL DEFAULT 'English',
    default_target_languages TEXT[] NOT NULL DEFAULT ARRAY['Tamil', 'Hindi'],
    email_notifications BOOLEAN NOT NULL DEFAULT TRUE,
    localization_complete BOOLEAN NOT NULL DEFAULT TRUE,
    weekly_digest BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Courses
CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    source_language TEXT NOT NULL,
    content_type TEXT NOT NULL CHECK (content_type IN ('pdf', 'video')),
    file_url TEXT,
    file_name TEXT,
    file_size INTEGER,
    local_file_path TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Content blocks (extracted from course files)
CREATE TABLE IF NOT EXISTS content_blocks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    block_number INTEGER NOT NULL,
    original_text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Localization jobs
CREATE TABLE IF NOT EXISTS localizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    target_language TEXT NOT NULL,
    ai_model TEXT NOT NULL DEFAULT 'claude-sonnet-4-6',
    status TEXT NOT NULL DEFAULT 'queued'
        CHECK (status IN ('queued', 'processing', 'completed', 'failed', 'approved')),
    progress_percentage INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Translated blocks
CREATE TABLE IF NOT EXISTS translated_blocks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    block_id UUID NOT NULL REFERENCES content_blocks(id) ON DELETE CASCADE,
    localization_id UUID NOT NULL REFERENCES localizations(id) ON DELETE CASCADE,
    translated_text TEXT NOT NULL,
    confidence_score TEXT NOT NULL DEFAULT 'medium'
        CHECK (confidence_score IN ('high', 'medium', 'low')),
    is_approved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_courses_user_id ON courses(user_id);
CREATE INDEX IF NOT EXISTS idx_content_blocks_course_id ON content_blocks(course_id);
CREATE INDEX IF NOT EXISTS idx_localizations_course_id ON localizations(course_id);
CREATE INDEX IF NOT EXISTS idx_localizations_status ON localizations(status);
CREATE INDEX IF NOT EXISTS idx_translated_blocks_localization_id ON translated_blocks(localization_id);
CREATE INDEX IF NOT EXISTS idx_translated_blocks_block_id ON translated_blocks(block_id);

-- Storage bucket (create via Supabase Dashboard or API)
-- Bucket name: course-files (public read optional)

-- Row Level Security (optional - backend uses service key)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE localizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_blocks ENABLE ROW LEVEL SECURITY;
ALTER TABLE translated_blocks ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
