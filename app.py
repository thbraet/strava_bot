import os
from datetime import datetime
from flask import Flask
from models import db, migrate, login_manager
from routes import main_bp, auth_bp, webhook_bp, user_bp
from config import config

def create_app(config_name=None):
    """Application factory function"""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    with app.app_context():
        db.create_all()

    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(webhook_bp)
    app.register_blueprint(user_bp)
    
    # Register custom template filters
    @app.template_filter('strftime')
    def _jinja2_filter_datetime(date, fmt=None):
        if fmt:
            return date.strftime(fmt)
        return date.strftime('%Y-%m-%d %H:%M:%S')
    
    @app.template_global('now')
    def _jinja2_global_now(format_str=None):
        now = datetime.utcnow()
        if format_str == 'year':
            return now.strftime('%Y')
        return now
    
    return app