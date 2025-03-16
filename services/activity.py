from datetime import datetime
from models import db
from models.activity_log import ActivityLog
from services.strava import hide_activity_from_feed, get_activity

def should_hide_from_feed(activity, user):
    """Determine if activity should be hidden based on type and duration"""
    activity_type = activity.get('type')
    elapsed_time = activity.get('elapsed_time', 0)
    
    # Get user-specific threshold for this activity type
    threshold = user.get_activity_threshold(activity_type)
    
    # Check if threshold exists for this activity type and if duration is below threshold
    if threshold and elapsed_time < threshold:
        return True
    
    return False

def process_activity(activity_id, user):
    """Process an activity for a user"""
    # Get fresh access token
    access_token = user.get_valid_token()
    
    # Get activity details
    activity = get_activity(activity_id, access_token)
    
    if not activity:
        print(f"Failed to fetch activity {activity_id} for user {user.id}")
        return False
    
    was_hidden = False
    # Check if we should hide this activity
    if should_hide_from_feed(activity, user):
        was_hidden = hide_activity_from_feed(activity_id, access_token)
        print(f"Activity {activity_id} for user {user.id} hidden: {was_hidden}")
    else:
        print(f"Activity {activity_id} for user {user.id} does not need to be hidden")
    
    # Log the processing
    log_activity_process(user, activity, was_hidden)
    
    return was_hidden

def log_activity_process(user, activity, was_hidden):
    """Log the activity processing for auditing"""
    log = ActivityLog(
        user_id=user.id,
        strava_activity_id=activity['id'],
        activity_type=activity.get('type', 'Unknown'),
        activity_name=activity.get('name', 'Unnamed Activity'),
        elapsed_time=activity.get('elapsed_time', 0),
        distance=activity.get('distance', 0),
        was_hidden=was_hidden
    )
    
    # Update user statistics
    user.activities_processed += 1
    if was_hidden:
        user.activities_hidden += 1
    user.last_activity_date = datetime.utcnow()
    
    db.session.add(log)
    db.session.commit()