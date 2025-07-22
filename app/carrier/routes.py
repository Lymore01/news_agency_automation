from flask import request, jsonify
from . import carrier_bp
from app.extensions import db
from app.models import DeliveryPerson

@carrier_bp.route("/", methods=['GET'])
def get_carriers():
    carriers = DeliveryPerson.query.all()
    if not carriers:
        return jsonify({'message': 'No carriers found.'}), 404

    results = [
    {
        "id": c.id,
        "name": c.name,
        "vehicle_type": c.vehicle_type,
        "vehicle_id": c.vehicle_id,
        "phone": c.phone,
        "hire_date": c.hire_date,
        "is_active": c.is_active,
        "latitude": c.latitude,
        "longitude": c.longitude
    }
    for c in carriers
    ]

    return jsonify(results)

@carrier_bp.route("/<int:id>", methods=['GET'])
def get_carrier(id):
    carrier = DeliveryPerson.query.get(id)

    if not carrier:
        return jsonify({'message': 'No carrier found.'}), 404
    
    result = {
        "id": carrier.id,
        "name": carrier.name,
        "vehicle_type": carrier.vehicle_type,
        "vehicle_id": carrier.vehicle_id,
        "phone": carrier.phone,
        "hire_date": carrier.hire_date,
        "is_active": carrier.is_active,
        "latitude": carrier.latitude,
        "longitude": carrier.longitude
    }
    return jsonify(result)

@carrier_bp.route("/", methods=['POST'])
def create_carrier():
    data = request.get_json()
    
    if not data or not all(key in data for key in ['name']):
        return jsonify({'message': 'Missing required fields'}), 400

    name = data['name']
    vehicle_type = data.get('vehicle_type', None)
    vehicle_id = data.get('vehicle_id', None)
    phone = data.get('phone', None)
    is_active = data.get('is_active', True)
    latitude = data.get('latitude', 0.0)
    longitude = data.get('longitude', 0.0)

    new_carrier = DeliveryPerson(
        name=name,
        vehicle_type=vehicle_type,
        vehicle_id=vehicle_id,
        phone=phone,
        is_active=is_active,
        latitude=latitude,
        longitude=longitude
    )

    try:
        # Add to the session and commit to the database
        db.session.add(new_carrier)
        db.session.commit()

        return jsonify({
            'message': 'Carrier created successfully',
            'carrier': {
                'id': new_carrier.id,
                'name': new_carrier.name,
                'vehicle_type': new_carrier.vehicle_type,
                'vehicle_id': new_carrier.vehicle_id,
                'phone': new_carrier.phone,
                'is_active': new_carrier.is_active,
                "latitude": new_carrier.latitude,
                "longitude": new_carrier.longitude
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred while creating the carrier', 'error': str(e)}), 500

@carrier_bp.route("/<int:id>", methods=['PUT'])
def update_carrier(id):
    data = request.get_json()

    carrier = DeliveryPerson.query.get(id)
    if not carrier:
        return jsonify({'message': 'Carrier not found'}), 404

    if 'name' in data:
        carrier.name = data['name']
    if 'vehicle_type' in data:
        carrier.vehicle_type = data['vehicle_type']
    if 'vehicle_id' in data:
        carrier.vehicle_id = data['vehicle_id']
    if 'phone' in data:
        carrier.phone = data['phone']
    if 'is_active' in data:
        carrier.is_active = data['is_active']
    if 'latitude' in data:
        carrier.latitude = data['latitude']
    if 'longitude' in data:
        carrier.longitude = data['longitude']

    try:
        db.session.commit()
        return jsonify({
            'message': 'Carrier updated successfully',
            'carrier': {
                'id': carrier.id,
                'name': carrier.name,
                'vehicle_type': carrier.vehicle_type,
                'vehicle_id': carrier.vehicle_id,
                'phone': carrier.phone,
                'is_active': carrier.is_active,
                "latitude": carrier.latitude,
                "longitude": carrier.longitude
            }
        }), 200
    except Exception as e:
        db.session.rollback() 
        return jsonify({'message': 'An error occurred while updating the carrier', 'error': str(e)}), 500

@carrier_bp.route("/<int:id>", methods=['DELETE'])
def delete_carrier(id):
    carrier = DeliveryPerson.query.get(id)
    if not carrier:
        return jsonify({'message': 'Carrier not found'}), 404

    try:
        db.session.delete(carrier)
        db.session.commit()
        return jsonify({'message': 'Carrier deleted successfully'}), 200
    except Exception as e:
        db.session.rollback() 
        return jsonify({'message': 'An error occurred while deleting the carrier', 'error': str(e)}), 500

@carrier_bp.route('/<int:carrier_id>/activate', methods=['PUT'])
def activate_carrier(carrier_id):
    carrier = DeliveryPerson.query.get_or_404(carrier_id)
    
    carrier.is_active = True
    db.session.commit()
    
    return jsonify({
        'message': 'Carrier activated successfully',
        'carrier': {
            'id': carrier.id,
            'name': carrier.name,
            'is_active': carrier.is_active
        }
    })

@carrier_bp.route('/<int:carrier_id>/deactivate', methods=['PUT'])
def deactivate_carrier(carrier_id):
    carrier = DeliveryPerson.query.get_or_404(carrier_id)
    
    carrier.is_active = False
    db.session.commit()
    
    return jsonify({
        'message': 'Carrier deactivated successfully',
        'carrier': {
            'id': carrier.id,
            'name': carrier.name,
            'is_active': carrier.is_active
        }
})

@carrier_bp.route('/update_location/<int:carrier_id>', methods=['POST'])
def update_carrier_location(carrier_id):
    data = request.get_json()

    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if latitude is None or longitude is None:
        return jsonify({'message': 'Latitude and Longitude are required'}), 400

 
    carrier = DeliveryPerson.query.get(carrier_id)
    if not carrier:
        return jsonify({'message': 'Carrier not found'}), 404

    carrier.latitude = latitude
    carrier.longitude = longitude
    db.session.commit()

    return jsonify({'message': 'Carrier location updated successfully'}), 200