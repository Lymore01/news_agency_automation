from flask import Blueprint

location_bp = Blueprint('location', __name__, url_prefix="/locations")

from . import routes