from datetime import datetime
from models import db
from models.activity_log import ActivityLog
from services.strava import hide_activity_from_feed, get_activity, get_athlete_activities, get_activity_streams, update_activity_title
from services.title_generator import generate_title_for_activity

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

def process_activity(activity_id, user, generate_title=True):
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
    
    # Generate and update title if requested
    if generate_title:
        generate_and_update_title(activity_id, activity, access_token)
    
    # Log the processing
    log_activity_process(user, activity, was_hidden)
    
    return was_hidden

def generate_and_update_title(activity_id, activity, access_token):
    """Generate and update the title for an activity"""
    try:
        # Get activity streams (detailed data)
        streams = get_activity_streams(activity_id, access_token)
        
        if not streams:
            print(f"Failed to fetch streams for activity {activity_id}")
            return False
        
        # Generate a descriptive title
        new_title = generate_title_for_activity(activity, streams)
        
        # Update the activity title
        success = update_activity_title(activity_id, access_token, new_title)
        
        if success:
            print(f"Updated title for activity {activity_id}: {new_title}")
        else:
            print(f"Failed to update title for activity {activity_id}")
            
        return success
    except Exception as e:
        print(f"Error generating/updating title for activity {activity_id}: {str(e)}")
        return False

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

def process_historic_activities(user, max_pages=5, generate_titles=True):
    """Process all historic activities for a user"""
    access_token = user.get_valid_token()
    processed_count = 0
    hidden_count = 0
    titled_count = 0
    
    # Fetch activities page by page
    for page in range(1, max_pages + 1):
        activities = get_athlete_activities(access_token, page=page)
        
        # If no activities or API error, break the loop
        if not activities or len(activities) == 0:
            break
            
        # Process each activity
        for activity in activities:
            activity_id = activity['id']
            # Get full activity details
            full_activity = get_activity(activity_id, access_token)
            
            if full_activity:
                # Check if we should hide this activity
                if should_hide_from_feed(full_activity, user):
                    was_hidden = hide_activity_from_feed(activity_id, access_token)
                    if was_hidden:
                        hidden_count += 1
                else:
                    was_hidden = False
                
                # Generate and update title if requested
                if generate_titles:
                    if generate_and_update_title(activity_id, full_activity, access_token):
                        titled_count += 1
                
                # Log the processing
                log_activity_process(user, full_activity, was_hidden)
                processed_count += 1
    
    return {
        'processed': processed_count,
        'hidden': hidden_count,
        'titled': titled_count
    }
