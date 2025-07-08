from datetime import datetime, time
import pytz
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database.models import ConversationMessage, ChatSession, ComplianceLog
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ComplianceService:
    """RBI and TRAI compliance service for debt collection"""
    
    def __init__(self):
        self.timezone = pytz.timezone(settings.TIMEZONE)
        self.max_daily_messages = settings.MAX_MESSAGES_PER_DAY
        self.business_start = time.fromisoformat(settings.BUSINESS_HOURS_START)
        self.business_end = time.fromisoformat(settings.BUSINESS_HOURS_END)

    async def check_message_compliance(
        self, 
        borrower_id: str, 
        platform: str, 
        db: AsyncSession
    ) -> Dict[str, any]:
        """Check if sending a message complies with regulations"""
        try:
            # Check daily message limit
            daily_limit_check = await self._check_daily_limit(borrower_id, platform, db)
            if not daily_limit_check["allowed"]:
                return daily_limit_check

            # Check business hours
            business_hours_check = self._check_business_hours()
            if not business_hours_check["allowed"]:
                return business_hours_check

            # Check opt-out status
            opt_out_check = await self._check_opt_out_status(borrower_id, db)
            if not opt_out_check["allowed"]:
                return opt_out_check

            return {"allowed": True, "reason": "Compliant"}

        except Exception as e:
            logger.error(f"Compliance check error: {e}")
            return {"allowed": False, "reason": "Compliance check failed"}

    async def _check_daily_limit(self, borrower_id: str, platform: str, db: AsyncSession) -> Dict:
        """Check daily message limit per borrower"""
        try:
            today = datetime.now(self.timezone).date()
            start_of_day = datetime.combine(today, time.min).replace(tzinfo=self.timezone)
            end_of_day = datetime.combine(today, time.max).replace(tzinfo=self.timezone)

            # Count messages sent today
            result = await db.execute(
                select(func.count(ConversationMessage.id))
                .join(ChatSession, ConversationMessage.session_id == ChatSession.id)
                .where(
                    ChatSession.borrower_id == borrower_id,
                    ChatSession.platform == platform,
                    ConversationMessage.sender_type == "bot",
                    ConversationMessage.sent_at >= start_of_day,
                    ConversationMessage.sent_at <= end_of_day
                )
            )
            
            message_count = result.scalar() or 0

            if message_count >= self.max_daily_messages:
                return {
                    "allowed": False,
                    "reason": f"Daily message limit ({self.max_daily_messages}) exceeded",
                    "count": message_count
                }

            return {"allowed": True, "count": message_count}

        except Exception as e:
            logger.error(f"Daily limit check error: {e}")
            return {"allowed": False, "reason": "Daily limit check failed"}

    def _check_business_hours(self) -> Dict:
        """Check if current time is within business hours"""
        try:
            current_time = datetime.now(self.timezone).time()
            
            if self.business_start <= current_time <= self.business_end:
                return {"allowed": True}
            else:
                return {
                    "allowed": False,
                    "reason": f"Outside business hours ({self.business_start} - {self.business_end})"
                }

        except Exception as e:
            logger.error(f"Business hours check error: {e}")
            return {"allowed": False, "reason": "Business hours check failed"}

    async def _check_opt_out_status(self, borrower_id: str, db: AsyncSession) -> Dict:
        """Check if borrower has opted out"""
        try:
            result = await db.execute(
                select(ComplianceLog)
                .where(
                    ComplianceLog.borrower_id == borrower_id,
                    ComplianceLog.action_type == "opt_out"
                )
                .order_by(ComplianceLog.created_at.desc())
                .limit(1)
            )
            
            opt_out_log = result.scalar_one_or_none()
            
            if opt_out_log:
                return {
                    "allowed": False,
                    "reason": "Borrower has opted out",
                    "opt_out_date": opt_out_log.created_at.isoformat()
                }

            return {"allowed": True}

        except Exception as e:
            logger.error(f"Opt-out check error: {e}")
            return {"allowed": False, "reason": "Opt-out check failed"}

    async def log_compliance_action(
        self,
        borrower_id: str,
        action_type: str,
        description: str,
        metadata: Dict = None,
        db: AsyncSession = None
    ):
        """Log compliance-related actions"""
        try:
            compliance_log = ComplianceLog(
                borrower_id=borrower_id,
                action_type=action_type,
                description=description,
                metadata=metadata or {}
            )
            
            db.add(compliance_log)
            await db.commit()
            
            logger.info(f"Compliance action logged: {action_type} for borrower {borrower_id}")

        except Exception as e:
            logger.error(f"Compliance logging error: {e}")

    async def handle_opt_out(self, borrower_id: str, platform: str, db: AsyncSession):
        """Handle borrower opt-out request"""
        try:
            await self.log_compliance_action(
                borrower_id=borrower_id,
                action_type="opt_out",
                description=f"Borrower opted out from {platform} communications",
                metadata={"platform": platform, "timestamp": datetime.utcnow().isoformat()},
                db=db
            )

            # Close active chat sessions
            result = await db.execute(
                select(ChatSession)
                .where(
                    ChatSession.borrower_id == borrower_id,
                    ChatSession.status == "active"
                )
            )
            
            active_sessions = result.scalars().all()
            for session in active_sessions:
                session.status = "closed"
                session.ended_at = datetime.utcnow()

            await db.commit()
            logger.info(f"Borrower {borrower_id} opted out successfully")

        except Exception as e:
            logger.error(f"Opt-out handling error: {e}")
            await db.rollback()

# Global instance
compliance_service = ComplianceService()
