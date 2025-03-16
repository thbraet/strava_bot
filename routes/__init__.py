from flask import Blueprint

# Create blueprints
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
webhook_bp = Blueprint('webhook', __name__, url_prefix='/webhook')
user_bp = Blueprint('user', __name__, url_prefix='/user')

# Import routes to register them with blueprints
from . import main, auth, webhook, user