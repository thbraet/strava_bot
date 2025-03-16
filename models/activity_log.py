from datetime import datetime
from . import db

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    strava_activity_id = db.Column(db.BigInteger)
    activity_type = db.Column(db.String(50))
    activity_name = db.Column(db.String(255))
    elapsed_time = db.Column(db.Integer)
    distance = db.Column(db.Float)
    was_hidden = db.Column(db.Boolean, default=False)
    processed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('activity_logs', lazy=True))