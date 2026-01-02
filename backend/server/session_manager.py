"""Session and Context Management for Omnichannel Continuity"""
import json
from datetime import datetime
from typing import Dict, Any

# In-memory session storage (use Redis/DB in production)
SESSIONS = {}

class SessionManager:
    @staticmethod
    def create_session(session_id: str, channel: str, citizen_id: str = None):
        """Create new session with context"""
        SESSIONS[session_id] = {
            "session_id": session_id,
            "citizen_id": citizen_id or "CIT001",
            "channel": channel,  # web, phone, whatsapp
            "applications": [],
            "conversation_history": [],
            "current_intent": None,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        }
        return SESSIONS[session_id]
    
    @staticmethod
    def get_session(session_id: str):
        """Retrieve session or create new one"""
        if session_id not in SESSIONS:
            return SessionManager.create_session(session_id, "web")
        SESSIONS[session_id]["last_activity"] = datetime.now().isoformat()
        return SESSIONS[session_id]
    
    @staticmethod
    def update_applications(session_id: str, application_items: list):
        """Update applications in session"""
        session = SessionManager.get_session(session_id)
        session["applications"] = application_items
        return session
    
    @staticmethod
    def switch_channel(session_id: str, new_channel: str):
        """Handle channel switching (web → phone → kiosk)"""
        session = SessionManager.get_session(session_id)
        old_channel = session["channel"]
        session["channel"] = new_channel
        session["conversation_history"].append({
            "event": "channel_switch",
            "from": old_channel,
            "to": new_channel,
            "timestamp": datetime.now().isoformat()
        })
        return session
    
    @staticmethod
    def add_conversation(session_id: str, role: str, message: str):
        """Track conversation for context"""
        session = SessionManager.get_session(session_id)
        session["conversation_history"].append({
            "role": role,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        return session
    
    @staticmethod
    def get_context_summary(session_id: str) -> str:
        """Generate context summary for agent"""
        session = SessionManager.get_session(session_id)
        app_count = len(session["applications"])
        last_intent = session.get("current_intent", "browsing")
        
        summary = f"Citizen {session['citizen_id']} on {session['channel']}. "
        if app_count > 0:
            summary += f"{app_count} applications in progress. "
        summary += f"Current activity: {last_intent}."
        return summary
