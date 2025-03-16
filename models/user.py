from datetime import datetime
import requests
from flask_login import UserMixin
from . import db, login_manager
from flask import current_app

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    strava_id = db.Column(db.Integer, unique=True)
    username = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    access_token = db.Column(db.String(100), nullable=True)
    refresh_token = db.Column(db.String(100), nullable=True)
    token_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User preferences
    run_threshold = db.Column(db.Integer, default=3600)    # Default 1 hour in seconds
    ride_threshold = db.Column(db.Integer, default=7200)   # Default 2 hours in seconds
    walk_threshold = db.Column(db.Integer, default=10800)  # Default 3 hours in seconds
    
    # Activity statistics
    activities_processed = db.Column(db.Integer, default=0)
    activities_hidden = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.DateTime, nullable=True)
    
    def get_valid_token(self):
        """Get a valid access token, refreshing if necessary"""
        now = datetime.utcnow()
        
        # Check if token is expired or about to expire
        if not self.token_expiry or self.token_expiry <= now:
            self.refresh_strava_token()
            
        return self.access_token
    
    def refresh_strava_token(self):
        """Refresh the Strava access token"""
        response = requests.post(
            'https://www.strava.com/oauth/token',
            data={
                'client_id': current_app.config['STRAVA_CLIENT_ID'],
                'client_secret': current_app.config['STRAVA_CLIENT_SECRET'],
                'refresh_token': self.refresh_token,
                'grant_type': 'refresh_token'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']
            self.token_expiry = datetime.utcfromtimestamp(data['expires_at'])
            db.session.commit()
            return True
        else:
            print(f"Token refresh failed for user {self.id}: {response.text}")
            return False

    def get_activity_threshold(self, activity_type):
        """Get threshold for a specific activity type"""
        if activity_type == 'Run':
            return self.run_threshold
        elif activity_type == 'Ride':
            return self.ride_threshold
        elif activity_type == 'Walk':
            return self.walk_threshold
        return None  # No threshold defined for this activity type

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))