from flask import Blueprint

subscription_bp = Blueprint('subscription', __name__, url_prefix="/subscriptions")

from . import routes