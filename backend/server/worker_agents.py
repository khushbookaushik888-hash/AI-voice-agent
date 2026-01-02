"""Worker Agents for Government/Public Sector Services"""
from mock_data import SERVICES, CITIZENS, BENEFITS, APPLICATIONS, REQUESTS
from session_manager import SessionManager
import random
from datetime import datetime

# Information Agent
async def search_services(function_name, tool_call_id, arguments, llm, context, result_callback):
    """Search services by category, name, or eligibility"""
    query = arguments.get("query", "").lower()
    category = arguments.get("category", "").lower()
    eligibility = arguments.get("eligibility", "").lower()
    
    results = []
    for service_id, service in SERVICES.items():
        if (query in service["name"].lower() or 
            category in service["category"].lower() or 
            query == ""):
            if eligibility in service.get("eligibility", "").lower() or eligibility == "":
                results.append(f"{service['name']} - {service_id}")
    
    if results:
        await result_callback(f"Found {len(results)} services: " + ", ".join(results[:5]))
    else:
        await result_callback("No services found matching your criteria.")


async def get_service_recommendations(function_name, tool_call_id, arguments, llm, context, result_callback):
    """Get personalized service recommendations"""
    citizen_id = arguments.get("citizen_id", "CIT001")
    
    citizen = CITIZENS.get(citizen_id, CITIZENS["CIT001"])
    history = citizen["service_history"]
    
    # Simple recommendation: suggest complementary services
    recommendations = []
    if any(sid in history for sid in ["SVC001", "SVC008"]):  # Applied for healthcare
        recommendations.extend(["SVC002", "SVC010"])  # Suggest education and housing
    if any(sid in history for sid in ["SVC002", "SVC007"]):  # Applied for education
        recommendations.extend(["SVC001", "SVC009"])  # Suggest healthcare and employment
    
    if not recommendations:
        recommendations = ["SVC005", "SVC006", "SVC010"]  # Default recommendations
    
    rec_text = ", ".join([f"{SERVICES[sid]['name']}" for sid in recommendations[:3] if sid in SERVICES])
    await result_callback(f"Based on your profile, I recommend: {rec_text}")


# Availability Agent
async def check_service_availability(function_name, tool_call_id, arguments, llm, context, result_callback):
    """Check service availability and status"""
    service_id = arguments.get("service_id", "")
    region = arguments.get("region", "all")
    
    if service_id not in SERVICES:
        await result_callback(f"Service {service_id} not found.")
        return
    
    service = SERVICES[service_id]
    availability = service["availability"]
    
    if region == "all":
        status = "Available" if availability["status"] == "active" else "Temporarily unavailable"
        await result_callback(f"{service['name']} is {status}. Next available: {availability.get('next_available', 'N/A')}.")
    else:
        status = availability.get(region, "unknown")
        await result_callback(f"{service['name']} status in {region}: {status}.")


# Application Agent
async def add_to_applications(function_name, tool_call_id, arguments, llm, context, result_callback):
    """Add services to applications with session tracking"""
    session_id = arguments.get("session_id", "default")
    service_id = arguments.get("service_id", "")
    
    if service_id not in SERVICES:
        await result_callback(f"Service {service_id} not found.")
        return
    
    # Check eligibility (simplified)
    service = SERVICES[service_id]
    if service["availability"]["status"] != "active":
        await result_callback(f"Sorry, {service['name']} is currently unavailable.")
        return
    
    if session_id not in APPLICATIONS:
        APPLICATIONS[session_id] = []
    
    APPLICATIONS[session_id].append({"service_id": service_id, "status": "draft"})
    
    # Update session
    SessionManager.update_applications(session_id, APPLICATIONS[session_id])
    SessionManager.add_conversation(session_id, "system", f"Added {service_id} to applications")
    
    await result_callback(f"Added {service['name']} to your applications.")


async def view_applications(function_name, tool_call_id, arguments, llm, context, result_callback):
    """View current applications with status info"""
    session_id = arguments.get("session_id", "default")
    
    if session_id not in APPLICATIONS or not APPLICATIONS[session_id]:
        await result_callback("You have no applications yet. Let me help you get started!")
        return
    
    items = []
    for item in APPLICATIONS[session_id]:
        service = SERVICES[item["service_id"]]
        status = item["status"]
        items.append(f"{service['name']} - Status: {status}")
    
    await result_callback(f"Your applications: {', '.join(items)}.")


# Benefits Agent
async def check_eligibility(function_name, tool_call_id, arguments, llm, context, result_callback):
    """Check eligibility for benefits"""
    citizen_id = arguments.get("citizen_id", "CIT001")
    benefit_type = arguments.get("benefit_type", "")
    
    citizen = CITIZENS.get(citizen_id, CITIZENS["CIT001"])
    
    # Simplified eligibility check
    eligible = False
    if benefit_type in BENEFITS:
        benefit = BENEFITS[benefit_type]
        if citizen["income"] <= benefit["max_income"] and citizen["age"] >= benefit["min_age"]:
            eligible = True
    
    if eligible:
        await result_callback(f"You are eligible for {benefit_type}. Additional benefits may apply.")
    else:
        await result_callback(f"You may not be eligible for {benefit_type} based on current criteria. Let me check alternatives.")


async def check_benefits_points(function_name, tool_call_id, arguments, llm, context, result_callback):
    """Check citizen benefits points with redemption options"""
    citizen_id = arguments.get("citizen_id", "CIT001")
    
    if citizen_id not in CITIZENS:
        await result_callback("Citizen not found.")
        return
    
    citizen = CITIZENS[citizen_id]
    points = citizen['benefits_points']
    tier = citizen['benefits_tier']
    
    # Calculate redemption value
    redemption_value = points * 10  # 1 point = ₹10 in benefits
    
    benefits = {
        "Platinum": "Priority processing, additional subsidies, extended support",
        "Gold": "Faster processing, 20% additional benefits",
        "Silver": "Standard benefits with 10% bonus",
        "Bronze": "Basic benefits with points earning"
    }
    
    benefit = benefits.get(tier, "")
    
    await result_callback(
        f"{citizen['name']}, you have {points} benefits points ({tier} tier) = ₹{redemption_value} value. "
        f"Benefits: {benefit}. Would you like to apply points to your applications?"
    )


# Application Agent (continued)
async def process_application(function_name, tool_call_id, arguments, llm, context, result_callback):
    """Process application submission"""
    session_id = arguments.get("session_id", "default")
    citizen_id = arguments.get("citizen_id", "CIT001")
    
    # Simulate application processing
    success = random.choice([True, True, True, False])  # 75% success rate
    
    if success:
        request_id = f"REQ{random.randint(10000, 99999)}"
        
        # Store request
        REQUESTS[request_id] = {
            "citizen_id": citizen_id,
            "applications": APPLICATIONS.get(session_id, []),
            "status": "submitted",
            "created_at": datetime.now().isoformat()
        }
        
        # Clear applications
        if session_id in APPLICATIONS:
            APPLICATIONS[session_id] = []
        
        await result_callback(f"Application submitted successfully! Request ID: {request_id}. You'll receive confirmation shortly.")
    else:
        await result_callback(f"Application submission failed. Please check your information and try again.")


# Delivery Agent
async def schedule_document_delivery(function_name, tool_call_id, arguments, llm, context, result_callback):
    """Schedule document delivery or office pickup"""
    request_id = arguments.get("request_id", "REQ12345")
    delivery_type = arguments.get("delivery_type", "home")
    date = arguments.get("date", "tomorrow")
    
    if delivery_type == "home":
        await result_callback(f"Documents for {request_id} scheduled for home delivery on {date}. Estimated delivery: 5-7 business days.")
    else:
        await result_callback(f"Documents for {request_id} ready for pickup at office on {date}. We'll notify you when it's ready.")


# Post-Service Support Agent
async def track_request(function_name, tool_call_id, arguments, llm, context, result_callback):
    """Track request status"""
    request_id = arguments.get("request_id", "")
    
    if request_id in REQUESTS:
        request = REQUESTS[request_id]
        status = request.get("status", "submitted")
        await result_callback(f"Request {request_id} status: {status}. Expected processing time: 7-10 business days.")
    else:
        statuses = ["Submitted", "Under review", "Approved", "Processing", "Completed"]
        status = random.choice(statuses)
        await result_callback(f"Request {request_id} status: {status}. Expected processing time: 7-10 business days.")


async def initiate_revision(function_name, tool_call_id, arguments, llm, context, result_callback):
    """Initiate application revision or update"""
    request_id = arguments.get("request_id", "")
    reason = arguments.get("reason", "update needed")
    action = arguments.get("action", "revision")  # revision or update
    
    revision_id = f"REV{random.randint(1000, 9999)}"
    
    # Update request status
    if request_id in REQUESTS:
        REQUESTS[request_id]["status"] = "revision_initiated" if action == "revision" else "update_initiated"
    
    if action == "revision":
        await result_callback(
            f"Revision initiated for request {request_id}. Revision ID: {revision_id}. "
            f"What changes would you like to make? I can guide you through the process."
        )
    else:
        await result_callback(
            f"Update initiated for request {request_id}. Update ID: {revision_id}. "
            f"You can submit additional documents or information. "
            f"We'll process the update within 3-5 business days."
        )


# Escalation
async def escalate_to_human(function_name, tool_call_id, arguments, llm, context, result_callback):
    """Escalate to human agent with context transfer"""
    session_id = arguments.get("session_id", "default")
    reason = arguments.get("reason", "general inquiry")
    
    # Get session context for human agent
    context_summary = SessionManager.get_context_summary(session_id)
    
    await result_callback(
        f"I'm connecting you to a human agent who can better assist with {reason}. "
        f"They'll have your conversation history and application details. Please hold."
    )


async def get_session_context(function_name, tool_call_id, arguments, llm, context, result_callback):
    """Retrieve session context for continuity"""
    session_id = arguments.get("session_id", "default")
    
    summary = SessionManager.get_context_summary(session_id)
    await result_callback(summary)
