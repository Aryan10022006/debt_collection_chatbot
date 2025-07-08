-- AI Debt Collection Chatbot Database Schema
-- Pure Python FastAPI Implementation

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS debt_collection_db;

-- Use the database
\c debt_collection_db;

-- Create debtors table
CREATE TABLE IF NOT EXISTS debtors (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(100),
    amount DECIMAL(12,2) NOT NULL,
    due_date DATE NOT NULL,
    language VARCHAR(20) DEFAULT 'Hindi',
    status VARCHAR(20) DEFAULT 'active',
    last_contact DATE,
    payment_history JSONB DEFAULT '[]',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create chat sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    id VARCHAR(50) PRIMARY KEY,
    debtor_id VARCHAR(50) REFERENCES debtors(id),
    channel VARCHAR(20) DEFAULT 'web', -- web, whatsapp, sms
    status VARCHAR(20) DEFAULT 'active',
    messages JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create chat messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id VARCHAR(50) PRIMARY KEY,
    session_id VARCHAR(50) REFERENCES chat_sessions(id),
    message_type VARCHAR(10) NOT NULL, -- user, bot, system
    content TEXT NOT NULL,
    language VARCHAR(20),
    ai_model VARCHAR(50),
    response_time DECIMAL(8,3),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create payments table
CREATE TABLE IF NOT EXISTS payments (
    id VARCHAR(50) PRIMARY KEY,
    debtor_id VARCHAR(50) REFERENCES debtors(id),
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    status VARCHAR(20) DEFAULT 'pending',
    payment_method VARCHAR(50),
    transaction_id VARCHAR(100),
    payment_url TEXT,
    processor VARCHAR(50) DEFAULT 'razorpay',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create analytics table
CREATE TABLE IF NOT EXISTS analytics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(12,2),
    metric_data JSONB,
    date DATE DEFAULT CURRENT_DATE,
    hour INTEGER DEFAULT EXTRACT(HOUR FROM CURRENT_TIMESTAMP),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_debtors_phone ON debtors(phone);
CREATE INDEX IF NOT EXISTS idx_debtors_status ON debtors(status);
CREATE INDEX IF NOT EXISTS idx_debtors_due_date ON debtors(due_date);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_debtor ON chat_sessions(debtor_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_channel ON chat_sessions(channel);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_payments_debtor ON payments(debtor_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_analytics_date ON analytics(date);
CREATE INDEX IF NOT EXISTS idx_analytics_metric ON analytics(metric_name);

-- Insert sample debtors
INSERT INTO debtors (id, name, phone, email, amount, due_date, language, status) VALUES
('AC123456789', 'राजेश कुमार', '+919876543210', 'rajesh.kumar@example.com', 25000.00, '2024-01-15', 'Hindi', 'active'),
('AC987654321', 'प्रिया शर्मा', '+919876543211', 'priya.sharma@example.com', 18500.00, '2024-01-20', 'Hindi', 'active'),
('AC555666777', 'अमित पटेल', '+919876543212', 'amit.patel@example.com', 35000.00, '2024-01-25', 'Hindi', 'active'),
('AC111222333', 'सुनीता देवी', '+919876543213', 'sunita.devi@example.com', 12000.00, '2024-01-30', 'Hindi', 'active'),
('AC444555666', 'विकास गुप्ता', '+919876543214', 'vikas.gupta@example.com', 28000.00, '2024-02-05', 'Hindi', 'active')
ON CONFLICT (id) DO NOTHING;

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
CREATE TRIGGER update_debtors_updated_at BEFORE UPDATE ON debtors FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO debt_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO debt_user;
