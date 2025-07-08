#!/usr/bin/env python3
"""
Database setup script for DebtBot AI
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from app.database.models import Base
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_tables():
    """Create all database tables"""
    try:
        engine = create_async_engine(settings.DATABASE_URL, echo=True)
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Database tables created successfully")
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        sys.exit(1)

async def seed_sample_data():
    """Seed database with sample data for testing"""
    from app.database.database import AsyncSessionLocal
    from app.database.models import Borrower, DebtAccount
    from decimal import Decimal
    from datetime import datetime, timedelta
    
    try:
        async with AsyncSessionLocal() as session:
            # Sample borrowers
            borrowers_data = [
                {
                    "account_number": "AC123456789",
                    "name": "राजेश कुमार",
                    "phone": "917439330282",
                    "email": "rajesh.kumar@email.com",
                    "preferred_language": "hi",
                    "address": "मुंबई, महाराष्ट्र"
                },
                {
                    "account_number": "AC987654321", 
                    "name": "Priya Sharma",
                    "phone": "919876543210",
                    "email": "priya.sharma@email.com",
                    "preferred_language": "en",
                    "address": "Bangalore, Karnataka"
                },
                {
                    "account_number": "AC456789123",
                    "name": "अर्जुन पटेल",
                    "phone": "918765432109",
                    "email": "arjun.patel@email.com", 
                    "preferred_language": "en-IN",
                    "address": "अहमदाबाद, गुजरात"
                }
            ]
            
            for borrower_data in borrowers_data:
                borrower = Borrower(**borrower_data)
                session.add(borrower)
                await session.flush()
                
                # Add debt account
                debt_account = DebtAccount(
                    borrower_id=borrower.id,
                    account_number=borrower_data["account_number"],
                    original_amount=Decimal("50000.00"),
                    outstanding_amount=Decimal("25000.00"),
                    due_date=datetime.now() + timedelta(days=30),
                    status="overdue",
                    interest_rate=Decimal("12.50")
                )
                session.add(debt_account)
            
            await session.commit()
            logger.info("✅ Sample data seeded successfully")
            
    except Exception as e:
        logger.error(f"❌ Data seeding failed: {e}")
        await session.rollback()

async def main():
    """Main setup function"""
    logger.info("🚀 Setting up DebtBot AI database...")
    
    await create_tables()
    await seed_sample_data()
    
    logger.info("🎉 Database setup completed successfully!")
    logger.info("You can now start the application with: uvicorn app.main:app --reload")

if __name__ == "__main__":
    asyncio.run(main())
