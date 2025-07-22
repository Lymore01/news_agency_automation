from flask import Blueprint

carrier_bp = Blueprint('carrier', __name__, url_prefix="/carriers")

from . import routes