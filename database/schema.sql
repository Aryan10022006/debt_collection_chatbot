-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Borrowers table
CREATE TABLE borrowers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_number VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    address TEXT,
    preferred_language VARCHAR(10) DEFAULT 'hi',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Debt accounts table
CREATE TABLE debt_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    borrower_id UUID REFERENCES borrowers(id) ON DELETE CASCADE,
    account_number VARCHAR(50) NOT NULL,
    original_amount DECIMAL(15,2) NOT NULL,
    outstanding_amount DECIMAL(15,2) NOT NULL,
    due_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'overdue', 'settled', 'legal', 'written_off')),
    interest_rate DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Campaigns table
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL CHECK (type IN ('payment_reminder', 'emi_offer', 'settlement', 'final_notice')),
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'paused', 'completed')),
    target_language VARCHAR(10),
    template_id UUID,
    scheduled_at TIMESTAMP WITH TIME ZONE,
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Message templates table
CREATE TABLE message_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    language VARCHAR(10) NOT NULL,
    type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    variables JSONB DEFAULT '[]',
    is_approved BOOLEAN DEFAULT false,
    whatsapp_template_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chat sessions table
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    borrower_id UUID REFERENCES borrowers(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(id),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    platform VARCHAR(20) NOT NULL CHECK (platform IN ('web', 'whatsapp', 'sms')),
    language VARCHAR(10) NOT NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'closed', 'transferred')),
    metadata JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Conversation messages table
CREATE TABLE conversation_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    sender_type VARCHAR(10) NOT NULL CHECK (sender_type IN ('user', 'bot', 'agent')),
    message_type VARCHAR(20) DEFAULT 'text' CHECK (message_type IN ('text', 'image', 'document', 'audio', 'video')),
    content TEXT NOT NULL,
    original_language VARCHAR(10),
    translated_content TEXT,
    metadata JSONB DEFAULT '{}',
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    delivered_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE
);

-- Campaign recipients table
CREATE TABLE campaign_recipients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    borrower_id UUID REFERENCES borrowers(id) ON DELETE CASCADE,
    debt_account_id UUID REFERENCES debt_accounts(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'delivered', 'read', 'replied', 'failed')),
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    replied_at TIMESTAMP WITH TIME ZONE,
    unique_link VARCHAR(255) UNIQUE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Payment transactions table
CREATE TABLE payment_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    debt_account_id UUID REFERENCES debt_accounts(id) ON DELETE CASCADE,
    session_id UUID REFERENCES chat_sessions(id),
    amount DECIMAL(15,2) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('payment', 'settlement', 'adjustment')),
    payment_method VARCHAR(50),
    transaction_id VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    processed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Analytics events table
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(50) NOT NULL,
    session_id UUID REFERENCES chat_sessions(id),
    borrower_id UUID REFERENCES borrowers(id),
    campaign_id UUID REFERENCES campaigns(id),
    properties JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Compliance logs table
CREATE TABLE compliance_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    borrower_id UUID REFERENCES borrowers(id) ON DELETE CASCADE,
    action_type VARCHAR(50) NOT NULL,
    description TEXT,
    performed_by UUID,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Language preferences table
CREATE TABLE language_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    borrower_id UUID REFERENCES borrowers(id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL,
    confidence_score DECIMAL(3,2) DEFAULT 0.0,
    detected_from VARCHAR(20) CHECK (detected_from IN ('manual', 'auto_detect', 'conversation')),
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_borrowers_phone ON borrowers(phone);
CREATE INDEX idx_borrowers_account_number ON borrowers(account_number);
CREATE INDEX idx_debt_accounts_status ON debt_accounts(status);
CREATE INDEX idx_debt_accounts_due_date ON debt_accounts(due_date);
CREATE INDEX idx_chat_sessions_token ON chat_sessions(session_token);
CREATE INDEX idx_chat_sessions_borrower ON chat_sessions(borrower_id);
CREATE INDEX idx_conversation_messages_session ON conversation_messages(session_id);
CREATE INDEX idx_campaign_recipients_campaign ON campaign_recipients(campaign_id);
CREATE INDEX idx_campaign_recipients_status ON campaign_recipients(status);
CREATE INDEX idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_events_timestamp ON analytics_events(timestamp);

-- Full-text search indexes
CREATE INDEX idx_borrowers_name_search ON borrowers USING gin(name gin_trgm_ops);
CREATE INDEX idx_conversation_content_search ON conversation_messages USING gin(content gin_trgm_ops);
