"""Analytics and Metrics Tracking for Service Performance"""
from datetime import datetime
from typing import Dict, List

ANALYTICS = {
    "total_conversations": 0,
    "total_orders": 0,
    "total_revenue": 0,
    "avg_order_value": 0,
    "conversion_rate": 0,
    "cart_abandonment": 0,
    "popular_products": {},
    "customer_satisfaction": [],
    "agent_performance": {
        "recommendation_agent": 0,
        "inventory_agent": 0,
        "payment_agent": 0,
        "loyalty_agent": 0,
        "fulfillment_agent": 0,
        "support_agent": 0
    }
}

class AnalyticsTracker:
    @staticmethod
    def track_conversation_start():
        """Track new conversation"""
        ANALYTICS["total_conversations"] += 1
    
    @staticmethod
    def track_order(order_value: float):
        """Track completed order"""
        ANALYTICS["total_orders"] += 1
        ANALYTICS["total_revenue"] += order_value
        ANALYTICS["avg_order_value"] = ANALYTICS["total_revenue"] / ANALYTICS["total_orders"]
        ANALYTICS["conversion_rate"] = (ANALYTICS["total_orders"] / ANALYTICS["total_conversations"]) * 100
    
    @staticmethod
    def track_product_view(sku: str):
        """Track product views"""
        if sku not in ANALYTICS["popular_products"]:
            ANALYTICS["popular_products"][sku] = 0
        ANALYTICS["popular_products"][sku] += 1
    
    @staticmethod
    def track_agent_call(agent_name: str):
        """Track worker agent usage"""
        if agent_name in ANALYTICS["agent_performance"]:
            ANALYTICS["agent_performance"][agent_name] += 1
    
    @staticmethod
    def track_cart_abandonment():
        """Track cart abandonment"""
        ANALYTICS["cart_abandonment"] += 1
    
    @staticmethod
    def track_satisfaction(rating: int):
        """Track customer satisfaction (1-5)"""
        ANALYTICS["customer_satisfaction"].append(rating)
    
    @staticmethod
    def get_metrics() -> Dict:
        """Get current analytics"""
        avg_satisfaction = sum(ANALYTICS["customer_satisfaction"]) / len(ANALYTICS["customer_satisfaction"]) if ANALYTICS["customer_satisfaction"] else 0
        
        return {
            "total_conversations": ANALYTICS["total_conversations"],
            "total_orders": ANALYTICS["total_orders"],
            "total_revenue": f"₹{ANALYTICS['total_revenue']:.2f}",
            "avg_order_value": f"₹{ANALYTICS['avg_order_value']:.2f}",
            "conversion_rate": f"{ANALYTICS['conversion_rate']:.2f}%",
            "avg_satisfaction": f"{avg_satisfaction:.2f}/5",
            "top_products": sorted(ANALYTICS["popular_products"].items(), key=lambda x: x[1], reverse=True)[:5],
            "agent_performance": ANALYTICS["agent_performance"]
        }
