# Human-like behavior patterns for SocialFlow AI
import random
from datetime import datetime, timedelta

# Posting frequency limits (in minutes)
POSTING_FREQUENCY = {
    "reddit": {"min_hours": 2, "max_hours": 8, "daily_limit": 3},
    "telegram": {"min_minutes": 15, "max_minutes": 120, "daily_limit": 5}, 
    "threads": {"min_hours": 1, "max_hours": 4, "daily_limit": 4},
    "instagram": {"min_hours": 4, "max_hours": 12, "daily_limit": 8}
}

# Daily engagement limits
ENGAGEMENT_LIMITS = {
    "daily_posts": 5,
    "daily_comments": 20,
    "daily_joins": 3,
    "hourly_actions": 8,
    "weekly_rest_days": 1
}

# Content variety distribution  
CONTENT_VARIETY = {
    "trading_insights": 0.4,
    "ai_discussion": 0.3, 
    "general_engagement": 0.2,
    "trending_topics": 0.1
}

# Realistic timing patterns
ACTIVITY_WINDOWS = {
    "morning": {"start": 9, "end": 11, "weight": 0.3},
    "afternoon": {"start": 14, "end": 16, "weight": 0.4}, 
    "evening": {"start": 19, "end": 21, "weight": 0.3}
}

# Delay patterns (seconds)
DELAYS = {
    "between_posts": {"min": 300, "max": 1800},  # 5-30 minutes
    "between_comments": {"min": 60, "max": 600},  # 1-10 minutes
    "reading_time": {"min": 10, "max": 60},       # 10-60 seconds
    "typing_simulation": {"min": 2, "max": 8}     # 2-8 seconds per 10 words
}

def get_realistic_delay(action_type: str) -> int:
    """Get realistic delay for given action type"""
    if action_type in DELAYS:
        return random.randint(DELAYS[action_type]["min"], DELAYS[action_type]["max"])
    return 60  # default 1 minute

def is_in_activity_window() -> bool:
    """Check if current time is in active posting window"""
    current_hour = datetime.now().hour
    for window in ACTIVITY_WINDOWS.values():
        if window["start"] <= current_hour <= window["end"]:
            return True
    return False

def get_daily_action_count(platform: str, action_type: str) -> int:
    """Get remaining actions allowed for today"""
    # This would integrate with activity tracking
    # For now, return conservative limits
    if action_type == "post":
        return POSTING_FREQUENCY[platform]["daily_limit"]
    elif action_type == "comment":
        return ENGAGEMENT_LIMITS["daily_comments"]
    return 0
