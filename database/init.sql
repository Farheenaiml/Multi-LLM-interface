-- Initialize databases for the Multi-LLM Broadcast Workspace

-- Create main application database
CREATE DATABASE IF NOT EXISTS broadcast_workspace;

-- Create LiteLLM database
CREATE DATABASE IF NOT EXISTS litellm;

-- Connect to broadcast_workspace database
\c broadcast_workspace;

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    total_cost DECIMAL(10,4) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active'
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id),
    pane_id VARCHAR(255),
    role VARCHAR(20),
    content TEXT,
    model_id VARCHAR(255),
    timestamp TIMESTAMP DEFAULT NOW(),
    provenance JSONB,
    metadata JSONB
);

-- Pipeline templates table
CREATE TABLE IF NOT EXISTS pipeline_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    steps JSONB NOT NULL,
    model_configurations JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    usage_count INTEGER DEFAULT 0
);

-- Metrics table
CREATE TABLE IF NOT EXISTS metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id),
    pane_id VARCHAR(255),
    model_id VARCHAR(255),
    tokens_used INTEGER,
    cost_usd DECIMAL(10,6),
    latency_ms INTEGER,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_pane_id ON messages(pane_id);
CREATE INDEX IF NOT EXISTS idx_metrics_session_id ON metrics(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);