from datetime import datetime
from flask import render_template, current_app
from . import main_bp
from services.strava import get_authorization_url

@main_bp.route('/')
def index():
    """Main landing page"""
    auth_url = get_authorization_url()
    return render_template('index.html', 
                           auth_url=auth_url,
                           client_id=current_app.config['STRAVA_CLIENT_ID'],
                           current_year=datetime.now().year)