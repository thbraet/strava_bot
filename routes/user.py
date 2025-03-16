from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import user_bp
from models import db
from models.activity_log import ActivityLog
from services.activity import process_historic_activities

@user_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with stats and settings"""
    # Get recent activity logs
    recent_logs = ActivityLog.query.filter_by(user_id=current_user.id)\
                                .order_by(ActivityLog.processed_at.desc())\
                                .limit(10).all()
    
    # Calculate stats
    total_processed = current_user.activities_processed
    total_hidden = current_user.activities_hidden
    hide_percentage = (total_hidden / total_processed * 100) if total_processed > 0 else 0
    
    return render_template(
        'dashboard.html',
        user=current_user,
        recent_logs=recent_logs,
        total_processed=total_processed,
        total_hidden=total_hidden,
        hide_percentage=hide_percentage
    )

@user_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings page"""
    if request.method == 'POST':
        # Update user preferences
        try:
            current_user.run_threshold = int(request.form.get('run_threshold', 3600))
            current_user.ride_threshold = int(request.form.get('ride_threshold', 7200))
            current_user.walk_threshold = int(request.form.get('walk_threshold', 10800))
            db.session.commit()
            flash('Settings updated successfully!', 'success')
        except ValueError:
            flash('Please enter valid values for thresholds', 'danger')
        
    return render_template('settings.html', user=current_user)

@user_bp.route('/process-historic-activities', methods=['POST'])
@login_required
def process_historic():
    """Process all historic activities for the current user"""
    try:
        result = process_historic_activities(current_user)
        flash(f"Processed {result['processed']} activities. {result['hidden']} were hidden from your feed.", 'success')
    except Exception as e:
        flash(f"Error processing activities: {str(e)}", 'danger')
    
    return redirect(url_for('user.dashboard'))
