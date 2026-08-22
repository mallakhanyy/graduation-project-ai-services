"""
Enhanced severity calculation with contextual factors.
"""

from typing import Dict, Any, Tuple
from datetime import datetime


class SeverityLevel:
    """Severity level constants."""
    VERY_CRITICAL = "حرجة جداً"
    CRITICAL = "حرجة"
    VERY_HIGH = "عالية جداً"
    HIGH = "عالية"
    MEDIUM = "متوسطة"
    LOW = "منخفضة"
    MINOR = "بسيطة"
    VERY_MINOR = "بسيطة جداً"
    NEGLIGIBLE = "غير مؤثرة"
    UNKNOWN = "غير معروفة"


def calculate_severity_enhanced(
    problem: str,
    confidence: float,
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Calculate severity with contextual factors.
    """
    if context is None:
        context = {}
    
    # 1. Get base severity and score
    base_severity, base_score = get_base_severity(problem, confidence)
    
    # 2. Apply contextual factors - returns factors and reasons separately
    factors, factor_reasons = calculate_factors(context)
    
    # 3. Calculate total score - all values are integers
    total_score = base_score + sum(factors.values())
    
    # 4. Clamp score between 0-100
    total_score = max(0, min(100, total_score))
    
    # 5. Get final severity
    final_severity = get_severity_from_score(total_score)
    
    # 6. Calculate urgency
    urgency = calculate_urgency(final_severity)
    
    # 7. Get recommended action
    action = get_recommended_action(final_severity)
    
    return {
        "level": final_severity,
        "score": total_score,
        "base_severity": base_severity,
        "base_score": base_score,
        "confidence": confidence,
        "factors": factors,
        "factor_reasons": factor_reasons,  # ← Stored separately
        "urgency": urgency,
        "recommended_action": action,
        "problem": problem,
        "timestamp": datetime.now().isoformat()
    }


def get_base_severity(problem: str, confidence: float) -> Tuple[str, int]:
    """Get base severity from problem and confidence."""
    if problem == "Pipe_Damage":
        if confidence >= 95:
            return SeverityLevel.VERY_CRITICAL, 100
        elif confidence >= 85:
            return SeverityLevel.CRITICAL, 85
        elif confidence >= 70:
            return SeverityLevel.HIGH, 70
        elif confidence >= 50:
            return SeverityLevel.MEDIUM, 55
        else:
            return SeverityLevel.LOW, 40
    
    elif problem == "Overflow":
        if confidence >= 95:
            return SeverityLevel.VERY_HIGH, 80
        elif confidence >= 85:
            return SeverityLevel.HIGH, 70
        elif confidence >= 70:
            return SeverityLevel.MEDIUM, 55
        elif confidence >= 50:
            return SeverityLevel.LOW, 40
        else:
            return SeverityLevel.MINOR, 30
    
    elif problem == "Blockage":
        if confidence >= 95:
            return SeverityLevel.MEDIUM, 55
        elif confidence >= 85:
            return SeverityLevel.LOW, 40
        elif confidence >= 70:
            return SeverityLevel.MINOR, 30
        elif confidence >= 50:
            return SeverityLevel.VERY_MINOR, 20
        else:
            return SeverityLevel.NEGLIGIBLE, 10
    
    return SeverityLevel.UNKNOWN, 0


def calculate_factors(context: Dict[str, Any]) -> Tuple[Dict[str, int], Dict[str, str]]:
    """
    Calculate factor scores based on context.
    
    Returns:
        Tuple of (factors_dict, reasons_dict)
        - factors_dict: factor name -> integer score (for calculation)
        - reasons_dict: factor name -> string reason (for display)
    """
    factors = {}
    reasons = {}
    now = datetime.now()
    
    # Time factor (night time = harder to repair)
    if now.hour < 6 or now.hour > 20:
        factors["time"] = 10
        reasons["time"] = "Night time (reduced visibility)"
    else:
        factors["time"] = 0
        reasons["time"] = ""
    
    # Weather factor
    weather = context.get('weather', 'clear')
    if weather in ['rain', 'storm']:
        factors["weather"] = 15
        reasons["weather"] = f"Bad weather ({weather})"
    elif weather == 'hot':
        factors["weather"] = 5
        reasons["weather"] = "Hot weather"
    else:
        factors["weather"] = 0
        reasons["weather"] = ""
    
    # Location factor
    location = context.get('location', 'field')
    if location == 'main_line':
        factors["location"] = 20
        reasons["location"] = "Main line (affects entire system)"
    elif location == 'secondary':
        factors["location"] = 10
        reasons["location"] = "Secondary line"
    else:
        factors["location"] = 0
        reasons["location"] = ""
    
    # Crop factor
    crop_stage = context.get('crop_stage', 'normal')
    if crop_stage in ['critical', 'flowering']:
        factors["crop"] = 15
        reasons["crop"] = f"Critical crop stage ({crop_stage})"
    else:
        factors["crop"] = 0
        reasons["crop"] = ""
    
    # Water factor
    water_availability = context.get('water_availability', 'normal')
    if water_availability == 'low':
        factors["water"] = 10
        reasons["water"] = "Water scarcity"
    else:
        factors["water"] = 0
        reasons["water"] = ""
    
    # Expertise factor
    expertise = context.get('user_expertise', 'medium')
    if expertise in ['low', 'none']:
        factors["expertise"] = 5
        reasons["expertise"] = "Low expertise (needs simpler instructions)"
    else:
        factors["expertise"] = 0
        reasons["expertise"] = ""
    
    # Season factor
    month = now.month
    if month in [3, 4, 5]:  # Spring
        factors["season"] = 10
        reasons["season"] = "Spring season (critical growth period)"
    elif month in [6, 7, 8]:  # Summer
        factors["season"] = 5
        reasons["season"] = "Summer season (high water demand)"
    else:
        factors["season"] = 0
        reasons["season"] = ""
    
    return factors, reasons


def get_severity_from_score(score: int) -> str:
    """Convert score back to severity level."""
    if score >= 95:
        return SeverityLevel.VERY_CRITICAL
    elif score >= 80:
        return SeverityLevel.CRITICAL
    elif score >= 70:
        return SeverityLevel.VERY_HIGH
    elif score >= 60:
        return SeverityLevel.HIGH
    elif score >= 45:
        return SeverityLevel.MEDIUM
    elif score >= 30:
        return SeverityLevel.LOW
    elif score >= 20:
        return SeverityLevel.MINOR
    elif score >= 10:
        return SeverityLevel.VERY_MINOR
    else:
        return SeverityLevel.NEGLIGIBLE


def calculate_urgency(severity: str) -> str:
    """Calculate urgency level."""
    urgency_map = {
        SeverityLevel.VERY_CRITICAL: "⚠️ IMMEDIATE - Within 1 hour",
        SeverityLevel.CRITICAL: "🔴 URGENT - Within 4 hours",
        SeverityLevel.VERY_HIGH: "🟠 HIGH - Within 12 hours",
        SeverityLevel.HIGH: "🟡 MEDIUM - Within 24 hours",
        SeverityLevel.MEDIUM: "🟢 LOW - Within 48 hours",
        SeverityLevel.LOW: "🔵 VERY LOW - Within 1 week",
        SeverityLevel.MINOR: "⚪ MINOR - Next maintenance",
        SeverityLevel.VERY_MINOR: "⚪ VERY MINOR - Schedule later",
        SeverityLevel.NEGLIGIBLE: "⚪ NEGLIGIBLE - Ignore",
    }
    return urgency_map.get(severity, "UNKNOWN")


def get_recommended_action(severity: str) -> str:
    """Get recommended action based on severity."""
    actions = {
        SeverityLevel.VERY_CRITICAL: "🚨 Call emergency repair team IMMEDIATELY",
        SeverityLevel.CRITICAL: "📞 Call repair team within 4 hours",
        SeverityLevel.VERY_HIGH: "📞 Schedule emergency repair within 12 hours",
        SeverityLevel.HIGH: "📋 Schedule repair within 24 hours",
        SeverityLevel.MEDIUM: "📋 Plan repair within 48 hours",
        SeverityLevel.LOW: "📝 Monitor and repair within 1 week",
        SeverityLevel.MINOR: "📝 Include in next maintenance",
        SeverityLevel.VERY_MINOR: "📝 Schedule when convenient",
        SeverityLevel.NEGLIGIBLE: "ℹ️ No action needed, continue monitoring",
    }
    return actions.get(severity, "Assess situation.")