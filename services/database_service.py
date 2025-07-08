"""
Database service for AI Debt Collection Chatbot
Pure Python implementation using SQLAlchemy and asyncpg
"""

import asyncio
import asyncpg
import json
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class Debtor:
    id: str
    name: str
    phone: str
    amount: float
    due_date: str
    language: str = "Hindi"
    status: str = "active"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@dataclass
class ChatSession:
    id: str
    debtor_id: str
    messages: List[Dict]
    created_at: str
    updated_at: str

class DatabaseService:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None
    
    async def initialize(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("Database connection pool initialized")
            await self.create_tables()
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            # Fallback to in-memory storage
            self.pool = None
    
    async def create_tables(self):
        """Create database tables if they don't exist"""
        if not self.pool:
            return
        
        create_tables_sql = """
        CREATE TABLE IF NOT EXISTS debtors (
            id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            phone VARCHAR(20) NOT NULL,
            amount DECIMAL(12,2) NOT NULL,
            due_date DATE NOT NULL,
            language VARCHAR(20) DEFAULT 'Hindi',
            status VARCHAR(20) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id VARCHAR(50) PRIMARY KEY,
            debtor_id VARCHAR(50) REFERENCES debtors(id),
            messages JSONB DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS chat_messages (
            id VARCHAR(50) PRIMARY KEY,
            session_id VARCHAR(50) REFERENCES chat_sessions(id),
            message_type VARCHAR(10) NOT NULL,
            content TEXT NOT NULL,
            language VARCHAR(20),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_debtors_phone ON debtors(phone);
        CREATE INDEX IF NOT EXISTS idx_chat_sessions_debtor ON chat_sessions(debtor_id);
        CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id);
        """
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(create_tables_sql)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
    
    async def get_debtor(self, debtor_id: str) -> Optional[Debtor]:
        """Get debtor by ID"""
        if not self.pool:
            return None
        
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM debtors WHERE id = $1", debtor_id
                )
                if row:
                    return Debtor(
                        id=row['id'],
                        name=row['name'],
                        phone=row['phone'],
                        amount=float(row['amount']),
                        due_date=row['due_date'].isoformat(),
                        language=row['language'],
                        status=row['status'],
                        created_at=row['created_at'].isoformat() if row['created_at'] else None,
                        updated_at=row['updated_at'].isoformat() if row['updated_at'] else None
                    )
        except Exception as e:
            logger.error(f"Failed to get debtor {debtor_id}: {e}")
        
        return None
    
    async def get_debtor_by_phone(self, phone: str) -> Optional[Debtor]:
        """Get debtor by phone number"""
        if not self.pool:
            return None
        
        try:
            # Clean phone number
            clean_phone = phone.replace("+", "").replace("-", "").replace(" ", "")
            
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM debtors WHERE REPLACE(REPLACE(REPLACE(phone, '+', ''), '-', ''), ' ', '') = $1", 
                    clean_phone
                )
                if row:
                    return Debtor(
                        id=row['id'],
                        name=row['name'],
                        phone=row['phone'],
                        amount=float(row['amount']),
                        due_date=row['due_date'].isoformat(),
                        language=row['language'],
                        status=row['status'],
                        created_at=row['created_at'].isoformat() if row['created_at'] else None,
                        updated_at=row['updated_at'].isoformat() if row['updated_at'] else None
                    )
        except Exception as e:
            logger.error(f"Failed to get debtor by phone {phone}: {e}")
        
        return None
    
    async def get_all_debtors(self) -> List[Debtor]:
        """Get all debtors"""
        if not self.pool:
            return []
        
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("SELECT * FROM debtors ORDER BY created_at DESC")
                return [
                    Debtor(
                        id=row['id'],
                        name=row['name'],
                        phone=row['phone'],
                        amount=float(row['amount']),
                        due_date=row['due_date'].isoformat(),
                        language=row['language'],
                        status=row['status'],
                        created_at=row['created_at'].isoformat() if row['created_at'] else None,
                        updated_at=row['updated_at'].isoformat() if row['updated_at'] else None
                    )
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Failed to get all debtors: {e}")
        
        return []
    
    async def save_chat_message(self, session_id: str, debtor_id: str, message_type: str, content: str, language: str = "Hindi"):
        """Save chat message to database"""
        if not self.pool:
            return
        
        try:
            async with self.pool.acquire() as conn:
                # Ensure session exists
                await conn.execute(
                    """
                    INSERT INTO chat_sessions (id, debtor_id, created_at, updated_at)
                    VALUES ($1, $2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    ON CONFLICT (id) DO UPDATE SET updated_at = CURRENT_TIMESTAMP
                    """,
                    session_id, debtor_id
                )
                
                # Save message
                message_id = f"msg_{datetime.now().timestamp()}"
                await conn.execute(
                    """
                    INSERT INTO chat_messages (id, session_id, message_type, content, language, timestamp)
                    VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP)
                    """,
                    message_id, session_id, message_type, content, language
                )
                
        except Exception as e:
            logger.error(f"Failed to save chat message: {e}")
    
    async def get_chat_history(self, session_id: str) -> List[Dict]:
        """Get chat history for a session"""
        if not self.pool:
            return []
        
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT message_type, content, language, timestamp
                    FROM chat_messages
                    WHERE session_id = $1
                    ORDER BY timestamp ASC
                    """,
                    session_id
                )
                
                return [
                    {
                        "type": row['message_type'],
                        "content": row['content'],
                        "language": row['language'],
                        "timestamp": row['timestamp'].isoformat()
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Failed to get chat history: {e}")
        
        return []
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Get system analytics"""
        if not self.pool:
            return {
                "total_debtors": 0,
                "total_sessions": 0,
                "total_messages": 0,
                "database_status": "disconnected"
            }
        
        try:
            async with self.pool.acquire() as conn:
                debtor_count = await conn.fetchval("SELECT COUNT(*) FROM debtors")
                session_count = await conn.fetchval("SELECT COUNT(*) FROM chat_sessions")
                message_count = await conn.fetchval("SELECT COUNT(*) FROM chat_messages")
                
                return {
                    "total_debtors": debtor_count,
                    "total_sessions": session_count,
                    "total_messages": message_count,
                    "database_status": "connected"
                }
        except Exception as e:
            logger.error(f"Failed to get analytics: {e}")
            return {
                "total_debtors": 0,
                "total_sessions": 0,
                "total_messages": 0,
                "database_status": "error"
            }
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
