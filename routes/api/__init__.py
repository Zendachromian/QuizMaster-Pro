from flask import Blueprint

# Create the main API blueprint
api_bp = Blueprint('api', __name__)

# Import and register all API route modules
from . import auth_routes
from . import user_routes  
from . import admin_routes