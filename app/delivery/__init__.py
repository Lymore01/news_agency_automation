from flask import Blueprint

delivery_bp = Blueprint('delivery', __name__, url_prefix="/deliveries")

from . import routes