"""
Analytics service for AI Debt Collection Chatbot
Pure Python implementation for tracking and reporting
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

@dataclass
class ChatMetrics:
    total_sessions: int
    total_messages: int
    avg_messages_per_session: float
    response_time_avg: float
    languages_used: Dict[str, int]
    peak_hours: Dict[str, int]

@dataclass
class DebtorMetrics:
    total_debtors: int
    active_debtors: int
    contacted_today: int
    payment_promises: int
    resolved_cases: int
    avg_debt_amount: float

@dataclass
class SystemMetrics:
    uptime: str
    memory_usage: float
    cpu_usage: float
    active_connections: int
    api_calls_today: int
    error_rate: float

class AnalyticsService:
    def __init__(self):
        self.session_data = defaultdict(list)
        self.message_counts = Counter()
        self.language_usage = Counter()
        self.hourly_activity = Counter()
        self.response_times = []
        self.api_calls = Counter()
        self.errors = Counter()
        self.start_time = datetime.now()
    
    def track_message(self, session_id: str, message_type: str, language: str, response_time: float = 0):
        """Track a chat message"""
        timestamp = datetime.now()
        
        # Track session activity
        self.session_data[session_id].append({
            "type": message_type,
            "language": language,
            "timestamp": timestamp.isoformat(),
            "response_time": response_time
        })
        
        # Update counters
        self.message_counts[message_type] += 1
        self.language_usage[language] += 1
        self.hourly_activity[timestamp.hour] += 1
        
        if response_time > 0:
            self.response_times.append(response_time)
    
    def track_api_call(self, endpoint: str, status_code: int, response_time: float):
        """Track API call metrics"""
        self.api_calls[endpoint] += 1
        
        if status_code >= 400:
            self.errors[endpoint] += 1
        
        # Track response time
        if response_time > 0:
            self.response_times.append(response_time)
    
    def get_chat_metrics(self) -> ChatMetrics:
        """Get chat-related metrics"""
        total_sessions = len(self.session_data)
        total_messages = sum(self.message_counts.values())
        
        avg_messages = total_messages / total_sessions if total_sessions > 0 else 0
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return ChatMetrics(
            total_sessions=total_sessions,
            total_messages=total_messages,
            avg_messages_per_session=round(avg_messages, 2),
            response_time_avg=round(avg_response_time, 2),
            languages_used=dict(self.language_usage),
            peak_hours=dict(self.hourly_activity)
        )
    
    def get_debtor_metrics(self, debtors_data: List[Dict]) -> DebtorMetrics:
        """Get debtor-related metrics"""
        total_debtors = len(debtors_data)
        active_debtors = len([d for d in debtors_data if d.get("status") == "active"])
        
        # Calculate contacted today (mock data for now)
        contacted_today = len([d for d in debtors_data if d.get("last_contact") == datetime.now().date().isoformat()])
        
        # Mock payment promises and resolved cases
        payment_promises = int(total_debtors * 0.3)  # 30% promise to pay
        resolved_cases = int(total_debtors * 0.15)   # 15% resolved
        
        # Calculate average debt amount
        amounts = [d.get("amount", 0) for d in debtors_data]
        avg_amount = sum(amounts) / len(amounts) if amounts else 0
        
        return DebtorMetrics(
            total_debtors=total_debtors,
            active_debtors=active_debtors,
            contacted_today=contacted_today,
            payment_promises=payment_promises,
            resolved_cases=resolved_cases,
            avg_debt_amount=round(avg_amount, 2)
        )
    
    def get_system_metrics(self, active_connections: int) -> SystemMetrics:
        """Get system-related metrics"""
        uptime = datetime.now() - self.start_time
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        
        # Mock system metrics (in production, use psutil)
        memory_usage = 45.2  # Mock memory usage percentage
        cpu_usage = 23.8     # Mock CPU usage percentage
        
        total_api_calls = sum(self.api_calls.values())
        total_errors = sum(self.errors.values())
        error_rate = (total_errors / total_api_calls * 100) if total_api_calls > 0 else 0
        
        return SystemMetrics(
            uptime=uptime_str,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            active_connections=active_connections,
            api_calls_today=total_api_calls,
            error_rate=round(error_rate, 2)
        )
    
    def get_hourly_activity(self) -> Dict[str, int]:
        """Get hourly activity distribution"""
        return dict(self.hourly_activity)
    
    def get_language_distribution(self) -> Dict[str, int]:
        """Get language usage distribution"""
        return dict(self.language_usage)
    
    def get_top_active_sessions(self, limit: int = 10) -> List[Dict]:
        """Get most active chat sessions"""
        session_activity = []
        
        for session_id, messages in self.session_data.items():
            session_activity.append({
                "session_id": session_id,
                "message_count": len(messages),
                "last_activity": messages[-1]["timestamp"] if messages else None,
                "languages": list(set(msg["language"] for msg in messages))
            })
        
        # Sort by message count
        session_activity.sort(key=lambda x: x["message_count"], reverse=True)
        return session_activity[:limit]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance-related metrics"""
        if not self.response_times:
            return {
                "avg_response_time": 0,
                "min_response_time": 0,
                "max_response_time": 0,
                "p95_response_time": 0
            }
        
        sorted_times = sorted(self.response_times)
        p95_index = int(len(sorted_times) * 0.95)
        
        return {
            "avg_response_time": round(sum(sorted_times) / len(sorted_times), 2),
            "min_response_time": round(min(sorted_times), 2),
            "max_response_time": round(max(sorted_times), 2),
            "p95_response_time": round(sorted_times[p95_index], 2)
        }
    
    def generate_daily_report(self, debtors_data: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive daily report"""
        chat_metrics = self.get_chat_metrics()
        debtor_metrics = self.get_debtor_metrics(debtors_data)
        system_metrics = self.get_system_metrics(len(self.session_data))
        performance_metrics = self.get_performance_metrics()
        
        return {
            "report_date": datetime.now().isoformat(),
            "chat_metrics": asdict(chat_metrics),
            "debtor_metrics": asdict(debtor_metrics),
            "system_metrics": asdict(system_metrics),
            "performance_metrics": performance_metrics,
            "top_sessions": self.get_top_active_sessions(5),
            "hourly_activity": self.get_hourly_activity(),
            "language_distribution": self.get_language_distribution()
        }
    
    def reset_daily_metrics(self):
        """Reset daily metrics (call this at midnight)"""
        self.api_calls.clear()
        self.errors.clear()
        self.hourly_activity.clear()
        logger.info("Daily metrics reset")
    
    def export_metrics(self, filepath: str):
        """Export metrics to JSON file"""
        try:
            metrics_data = {
                "export_timestamp": datetime.now().isoformat(),
                "session_data": dict(self.session_data),
                "message_counts": dict(self.message_counts),
                "language_usage": dict(self.language_usage),
                "hourly_activity": dict(self.hourly_activity),
                "api_calls": dict(self.api_calls),
                "errors": dict(self.errors),
                "response_times": self.response_times
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(metrics_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Metrics exported to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
