from flask import Blueprint

publication_bp = Blueprint('publication', __name__, url_prefix="/publications")

from . import routes