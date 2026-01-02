# Mock data for government/public sector demo

SERVICES = {
    "SVC001": {"name": "Healthcare Subsidy Program", "category": "Healthcare", "eligibility": "Low income families", "availability": {"status": "active", "next_available": "N/A"}},
    "SVC002": {"name": "Education Grant Application", "category": "Education", "eligibility": "Students under 25", "availability": {"status": "active", "next_available": "N/A"}},
    "SVC003": {"name": "Passport Renewal Service", "category": "Identification", "eligibility": "Citizens 18+", "availability": {"status": "active", "next_available": "N/A"}},
    "SVC004": {"name": "Housing Assistance Program", "category": "Housing", "eligibility": "Low to middle income", "availability": {"status": "active", "next_available": "N/A"}},
    "SVC005": {"name": "Unemployment Benefits", "category": "Employment", "eligibility": "Recently unemployed", "availability": {"status": "active", "next_available": "N/A"}},
    "SVC006": {"name": "Senior Citizen Support", "category": "Social Services", "eligibility": "Citizens 60+", "availability": {"status": "active", "next_available": "N/A"}},
    "SVC007": {"name": "Business License Application", "category": "Business", "eligibility": "Business owners", "availability": {"status": "active", "next_available": "N/A"}},
    "SVC008": {"name": "Child Care Subsidy", "category": "Family Services", "eligibility": "Families with children", "availability": {"status": "active", "next_available": "N/A"}},
    "SVC009": {"name": "Disability Support Services", "category": "Healthcare", "eligibility": "Persons with disabilities", "availability": {"status": "active", "next_available": "N/A"}},
    "SVC010": {"name": "Environmental Grant", "category": "Environment", "eligibility": "Organizations", "availability": {"status": "active", "next_available": "N/A"}},
    "SVC011": {"name": "Skill Training Program", "category": "Education", "eligibility": "Unemployed adults", "availability": {"status": "active", "next_available": "N/A"}},
    "SVC012": {"name": "Tax Filing Assistance", "category": "Financial", "eligibility": "Taxpayers", "availability": {"status": "active", "next_available": "N/A"}},
}

CITIZENS = {
    "CIT001": {"name": "Priya Sharma", "benefits_tier": "Gold", "benefits_points": 2500, "service_history": ["SVC001", "SVC005"], "income": 300000, "age": 35, "channel": "web"},
    "CIT002": {"name": "Rahul Verma", "benefits_tier": "Silver", "benefits_points": 1200, "service_history": ["SVC003", "SVC007"], "income": 500000, "age": 42, "channel": "phone"},
    "CIT003": {"name": "Anita Desai", "benefits_tier": "Platinum", "benefits_points": 5000, "service_history": ["SVC004", "SVC008", "SVC010"], "income": 200000, "age": 28, "channel": "whatsapp"},
    "CIT004": {"name": "Vikram Singh", "benefits_tier": "Bronze", "benefits_points": 500, "service_history": ["SVC002"], "income": 600000, "age": 55, "channel": "kiosk"},
    "CIT005": {"name": "Sneha Patel", "benefits_tier": "Gold", "benefits_points": 3200, "service_history": ["SVC006", "SVC009"], "income": 250000, "age": 31, "channel": "web"},
    "CIT006": {"name": "Arjun Mehta", "benefits_tier": "Silver", "benefits_points": 1800, "service_history": ["SVC001", "SVC002", "SVC009"], "income": 400000, "age": 38, "channel": "phone"},
    "CIT007": {"name": "Kavya Reddy", "benefits_tier": "Gold", "benefits_points": 2900, "service_history": ["SVC004", "SVC010"], "income": 350000, "age": 29, "channel": "web"},
    "CIT008": {"name": "Rohan Gupta", "benefits_tier": "Platinum", "benefits_points": 6500, "service_history": ["SVC003", "SVC005", "SVC007"], "income": 150000, "age": 45, "channel": "whatsapp"},
    "CIT009": {"name": "Meera Iyer", "benefits_tier": "Bronze", "benefits_points": 300, "service_history": [], "income": 700000, "age": 62, "channel": "kiosk"},
    "CIT010": {"name": "Siddharth Joshi", "benefits_tier": "Silver", "benefits_points": 1500, "service_history": ["SVC006", "SVC012"], "income": 450000, "age": 33, "channel": "web"},
}

BENEFITS = {
    "healthcare_subsidy": {"max_income": 400000, "min_age": 0, "description": "Healthcare cost subsidy"},
    "education_grant": {"max_income": 500000, "min_age": 18, "description": "Education funding support"},
    "housing_assistance": {"max_income": 600000, "min_age": 21, "description": "Housing support program"},
    "unemployment_benefits": {"max_income": 300000, "min_age": 18, "description": "Job loss financial aid"},
    "senior_support": {"max_income": 1000000, "min_age": 60, "description": "Elderly care services"},
    "disability_support": {"max_income": 800000, "min_age": 0, "description": "Disability assistance"},
}

APPLICATIONS = {}  # {session_id: [{"service_id": "SVC001", "status": "draft"}]}

REQUESTS = {}  # {request_id: {"citizen_id": "CIT001", "applications": [], "status": "submitted"}}
