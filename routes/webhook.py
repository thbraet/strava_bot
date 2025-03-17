from flask import request, jsonify, current_app
from . import webhook_bp
from models.user import User
from services.activity import process_activity

@webhook_bp.route('/', methods=['GET'])
def validate():
    """Respond to Strava's webhook validation request"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    print(request.args)
    print(challenge)
    
    if mode and token:
        if mode == 'subscribe' and token == current_app.config['STRAVA_VERIFICATION_TOKEN']:
            return jsonify({'hub.challenge': challenge})
    
    return 'Verification failed', 403

@webhook_bp.route('/', methods=['POST'])
def event():
    """Process incoming webhook events from Strava"""
    data = request.json
    
    # Only process new activities
    if data['object_type'] == 'activity' and data['aspect_type'] == 'create':
        activity_id = data['object_id']
        strava_user_id = data['owner_id']
        
        # Find the user
        user = User.query.filter_by(strava_id=strava_user_id).first()
        
        if user:
            process_activity(activity_id, user)
        else:
            print(f"User with Strava ID {strava_user_id} not found")
    
    return '', 200