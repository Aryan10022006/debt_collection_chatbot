from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, Decimal, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

Base = declarative_base()

class Borrower(Base):
    __tablename__ = "borrowers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_number = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False, index=True)
    email = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    preferred_language = Column(String(10), default="hi")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    debt_accounts = relationship("DebtAccount", back_populates="borrower")
    chat_sessions = relationship("ChatSession", back_populates="borrower")
    language_preferences = relationship("LanguagePreference", back_populates="borrower")

class DebtAccount(Base):
    __tablename__ = "debt_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    borrower_id = Column(UUID(as_uuid=True), ForeignKey("borrowers.id"), nullable=False)
    account_number = Column(String(50), nullable=False)
    original_amount = Column(Decimal(15, 2), nullable=False)
    outstanding_amount = Column(Decimal(15, 2), nullable=False)
    due_date = Column(DateTime, nullable=False)
    status = Column(String(20), default="active")  # active, overdue, settled, legal
    interest_rate = Column(Decimal(5, 2), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    borrower = relationship("Borrower", back_populates="debt_accounts")
    payment_transactions = relationship("PaymentTransaction", back_populates="debt_account")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    borrower_id = Column(UUID(as_uuid=True), ForeignKey("borrowers.id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    platform = Column(String(20), nullable=False)  # web, whatsapp, sms
    language = Column(String(10), nullable=False)
    status = Column(String(20), default="active")  # active, closed, transferred
    metadata = Column(JSON, default=dict)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    borrower = relationship("Borrower", back_populates="chat_sessions")
    messages = relationship("ConversationMessage", back_populates="session")

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False)
    sender_type = Column(String(10), nullable=False)  # user, bot, agent
    message_type = Column(String(20), default="text")  # text, image, document
    content = Column(Text, nullable=False)
    original_language = Column(String(10), nullable=True)
    translated_content = Column(Text, nullable=True)
    metadata = Column(JSON, default=dict)
    sent_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")

class LanguagePreference(Base):
    __tablename__ = "language_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    borrower_id = Column(UUID(as_uuid=True), ForeignKey("borrowers.id"), nullable=False)
    language_code = Column(String(10), nullable=False)
    confidence_score = Column(Decimal(3, 2), default=0.0)
    detected_from = Column(String(20))  # manual, auto_detect, conversation
    last_used_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    borrower = relationship("Borrower", back_populates="language_preferences")

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    debt_account_id = Column(UUID(as_uuid=True), ForeignKey("debt_accounts.id"), nullable=False)
    amount = Column(Decimal(15, 2), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # payment, settlement
    payment_method = Column(String(50), nullable=True)
    transaction_id = Column(String(255), nullable=True)
    status = Column(String(20), default="pending")  # pending, completed, failed
    processed_at = Column(DateTime, nullable=True)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    debt_account = relationship("DebtAccount", back_populates="payment_transactions")

class ComplianceLog(Base):
    __tablename__ = "compliance_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    borrower_id = Column(UUID(as_uuid=True), ForeignKey("borrowers.id"), nullable=False)
    action_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(50), nullable=False)
    session_id = Column(UUID(as_uuid=True), nullable=True)
    borrower_id = Column(UUID(as_uuid=True), nullable=True)
    properties = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow)
