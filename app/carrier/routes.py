from flask import request, jsonify
from . import carrier_bp
from app.extensions import db
from app.models import DeliveryPerson

