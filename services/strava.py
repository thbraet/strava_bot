import requests
from flask import current_app, url_for
from datetime import datetime
from models import db
from models.user import User

def get_authorization_url():
    """Generate the Strava authorization URL"""
    redirect_uri = url_for('auth.callback', _external=True)
    print("Strava client id: ", current_app.config['STRAVA_CLIENT_ID'])

    client_id = current_app.config['STRAVA_CLIENT_ID']
    
    auth_url = f"https://www.strava.com/oauth/authorize"
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'activity:write,activity:read_all'
    }
    
    return f"{auth_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"

def exchange_token(code):
    """Exchange authorization code for tokens"""
    client_id = current_app.config['STRAVA_CLIENT_ID']
    client_secret = current_app.config['STRAVA_CLIENT_SECRET']
    
    response = requests.post(
        'https://www.strava.com/oauth/token',
        data={
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code'
        }
    )
    
    if response.status_code != 200:
        return None
        
    return response.json()

def get_activity(activity_id, access_token):
    """Get activity details from Strava"""
    response = requests.get(
        f"https://www.strava.com/api/v3/activities/{activity_id}",
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    if response.status_code != 200:
        return None
        
    return response.json()

def get_activity_streams(activity_id, access_token, stream_types=None):
    """Get activity streams (detailed data) from Strava"""
    if stream_types is None:
        stream_types = ['time', 'heartrate', 'velocity_smooth', 'altitude', 'cadence', 'watts', 'grade_smooth']
    
    response = requests.get(
        f"https://www.strava.com/api/v3/activities/{activity_id}/streams",
        headers={'Authorization': f'Bearer {access_token}'},
        params={
            'keys': ','.join(stream_types),
            'key_by_type': True
        }
    )
    
    if response.status_code != 200:
        return None
        
    return response.json()

def get_athlete_activities(access_token, page=1, per_page=30):
    """Get athlete activities from Strava"""
    response = requests.get(
        "https://www.strava.com/api/v3/athlete/activities",
        headers={'Authorization': f'Bearer {access_token}'},
        params={
            'page': page,
            'per_page': per_page
        }
    )
    
    if response.status_code != 200:
        return None
        
    return response.json()

def hide_activity_from_feed(activity_id, access_token):
    """Set the 'hide_from_home' flag to true for an activity"""
    url = f"https://www.strava.com/api/v3/activities/{activity_id}"
    
    response = requests.put(
        url,
        headers={'Authorization': f'Bearer {access_token}'},
        json={'hide_from_home': True}
    )
    
    return response.status_code == 200

def update_activity_title(activity_id, access_token, title):
    """Update the title of an activity"""
    url = f"https://www.strava.com/api/v3/activities/{activity_id}"
    
    response = requests.put(
        url,
        headers={'Authorization': f'Bearer {access_token}'},
        json={'name': title}
    )
    
    return response.status_code == 200

def register_webhook():
    """Register the Strava webhook (used during setup)"""
    client_id = current_app.config['STRAVA_CLIENT_ID']
    client_secret = current_app.config['STRAVA_CLIENT_SECRET']
    verification_token = current_app.config['STRAVA_VERIFICATION_TOKEN']
    callback_url = url_for('webhook.event', _external=True)
    
    response = requests.post(
        'https://www.strava.com/api/v3/push_subscriptions',
        data={
            'client_id': client_id,
            'client_secret': client_secret,
            'callback_url': callback_url,
            'verify_token': verification_token
        }
    )
    
    return response.json() if response.status_code in (200, 201) else None

def process_user_from_token_response(data):
    """Process Strava token response and create or update user"""
    strava_id = data['athlete']['id']
    
    # Check if user already exists
    try:
        user = User.query.filter_by(strava_id=strava_id).first()
    except:
        user = None
    
    if not user:
        # Create new user
        user = User(
            strava_id=strava_id,
            username=data['athlete'].get('username'),
            email=None,  # Strava doesn't provide email in this response
            access_token=data['access_token'],
            refresh_token=data['refresh_token'],
            token_expiry=datetime.utcfromtimestamp(data['expires_at'])
        )
        db.session.add(user)
    else:
        # Update existing user's tokens
        user.access_token = data['access_token']
        user.refresh_token = data['refresh_token']
        user.token_expiry = datetime.utcfromtimestamp(data['expires_at'])
    
    db.session.commit()
    return user
