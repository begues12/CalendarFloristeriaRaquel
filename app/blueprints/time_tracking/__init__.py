"""
Blueprint de control de horarios
"""

from flask import Blueprint

bp = Blueprint('time_tracking', __name__)

from . import routes
