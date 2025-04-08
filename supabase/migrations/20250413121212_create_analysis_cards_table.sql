-- Create analysis_cards table
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS analysis_cards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    figma_file_key TEXT NOT NULL,
    node_id TEXT,
    title TEXT NOT NULL,
    description TEXT,
    severity TEXT,
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
); 