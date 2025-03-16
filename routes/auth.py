from flask import redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from . import auth_bp
from services.strava import exchange_token, process_user_from_token_response, get_authorization_url

@auth_bp.route('/authorize')
def authorize():
    """Redirect to Strava authorization page"""
    auth_url = get_authorization_url()
    return redirect(auth_url)

@auth_bp.route('/callback')
def callback():
    """Handle authorization callback from Strava"""
    error = request.args.get('error')
    if error:
        flash(f"Authorization failed: {error}", "danger")
        return redirect(url_for('main.index'))
    
    code = request.args.get('code')
    if not code:
        flash("No authorization code received", "danger")
        return redirect(url_for('main.index'))
    
    # Exchange code for tokens
    data = exchange_token(code)
    
    if not data:
        flash(f"Failed to authorize with Strava", "danger")
        return redirect(url_for('main.index'))
    
    # Process the response
    user = process_user_from_token_response(data)
    
    # Log the user in
    login_user(user)
    flash("Successfully connected to Strava!", "success")
    return redirect(url_for('user.dashboard'))

@auth_bp.route('/logout')
@login_required
def logout():
    """Log user out"""
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for('main.index'))