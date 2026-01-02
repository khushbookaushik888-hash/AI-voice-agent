"""Multilingual AI Voice Agent Orchestrator - Manages multi-agent workflow"""
from session_manager import SessionManager
from typing import Dict, Any

class VoiceAgentOrchestrator:
    """Orchestrates conversation flow and delegates to worker agents"""
    
    @staticmethod
    def analyze_intent(message: str, session_id: str) -> Dict[str, Any]:
        """Analyze user intent and determine which worker agents to engage"""
        message_lower = message.lower()
        session = SessionManager.get_session(session_id)
        
        intent = {
            "primary": None,
            "agents_needed": [],
            "context": session
        }
        
        # Service discovery intent
        if any(word in message_lower for word in ["looking for", "show me", "need", "want", "search", "find", "services"]):
            intent["primary"] = "service_discovery"
            intent["agents_needed"] = ["information_agent", "availability_agent"]
        
        # Application management intent
        elif any(word in message_lower for word in ["application", "apply", "form", "submit", "request"]):
            intent["primary"] = "application_management"
            intent["agents_needed"] = ["application_agent", "benefits_agent"]
        
        # Service request intent
        elif any(word in message_lower for word in ["submit", "complete", "process", "register", "enroll"]):
            intent["primary"] = "service_request"
            intent["agents_needed"] = ["application_agent", "delivery_agent", "benefits_agent"]
        
        # Post-service intent
        elif any(word in message_lower for word in ["track", "status", "update", "follow-up", "feedback"]):
            intent["primary"] = "post_service"
            intent["agents_needed"] = ["support_agent", "delivery_agent"]
        
        # Eligibility inquiry
        elif any(word in message_lower for word in ["eligible", "qualify", "requirements", "criteria", "benefits"]):
            intent["primary"] = "eligibility_inquiry"
            intent["agents_needed"] = ["benefits_agent", "information_agent"]
        
        # General browsing
        else:
            intent["primary"] = "general_inquiry"
            intent["agents_needed"] = ["information_agent"]
        
        # Update session intent
        session["current_intent"] = intent["primary"]
        
        return intent
    
    @staticmethod
    def get_conversation_strategy(intent: str) -> str:
        """Get service strategy based on intent"""
        strategies = {
            "service_discovery": "Ask open-ended questions about needs, eligibility, and preferences. Suggest 2-3 relevant services.",
            "application_management": "Confirm details, suggest additional services, mention available benefits.",
            "service_request": "Summarize request, check eligibility, provide submission options, ensure smooth process.",
            "post_service": "Show empathy, provide quick updates, offer alternatives if needed.",
            "eligibility_inquiry": "Highlight requirements, mention available benefits, suggest qualifying services.",
            "general_inquiry": "Be helpful, guide toward services, understand needs through questions."
        }
        return strategies.get(intent, "Be citizen-centric and helpful.")
    
    @staticmethod
    def should_suggest_additional_service(session_id: str) -> bool:
        """Determine if additional service suggestion opportunity exists"""
        session = SessionManager.get_session(session_id)
        applications = session.get("applications", [])
        
        # Suggest if 1-2 applications (not too few, not too many)
        return 1 <= len(applications) <= 2
    
    @staticmethod
    def get_additional_service_suggestion(session_id: str) -> str:
        """Generate contextual additional service suggestion"""
        from mock_data import SERVICES, APPLICATIONS
        
        session = SessionManager.get_session(session_id)
        app_items = APPLICATIONS.get(session_id, [])
        
        if not app_items:
            return ""
        
        # Analyze application categories
        categories = set()
        for item in app_items:
            if item["service_id"] in SERVICES:
                categories.add(SERVICES[item["service_id"]]["category"])
        
        suggestions = {
            "Healthcare": "Would you like to apply for our supplemental health benefits? We have programs that complement your current application!",
            "Education": "These would pair well with our education grants! Can I show you some matching scholarship options?",
            "Housing": "Don't forget housing assistance! A subsidy or loan would complete your support package.",
            "Employment": "Add some training programs to complete your application - we have excellent options!",
            "Transportation": "This pairs perfectly with our mobility assistance programs.",
        }
        
        for category in categories:
            if category in suggestions:
                return suggestions[category]
        
        return "Would you like to see additional services that might benefit you?"
    
    @staticmethod
    def handle_concern(concern_type: str, context: Dict) -> str:
        """Handle common citizen concerns"""
        responses = {
            "eligibility": "I understand. Let me check your eligibility requirements and available alternatives for you.",
            "documentation": "This service has clear documentation guidelines. I can guide you through the required documents.",
            "waiting_time": "We have options for expedited processing. I can also provide detailed timeline guidance.",
            "delivery": "We offer multiple delivery options including digital certificates and physical mail.",
            "comparison": "Let me show you how this service compares with alternatives in terms of benefits.",
        }
        return responses.get(concern_type, "I understand your concern. Let me help you with that.")
    
    @staticmethod
    def generate_closing_statement(session_id: str) -> str:
        """Generate appropriate closing based on session state"""
        session = SessionManager.get_session(session_id)
        intent = session.get("current_intent")
        
        closings = {
            "service_request": "Thank you for your application! You'll receive confirmation shortly. Is there anything else I can help with?",
            "service_discovery": "Would you like to apply for any of these services, or shall I show you more options?",
            "application_management": "Your application is ready! Would you like to proceed with submission?",
            "post_service": "I'm glad I could help! Feel free to reach out if you need anything else.",
        }
        
        return closings.get(intent, "Is there anything else I can help you with today?")
