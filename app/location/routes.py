from flask import request, jsonify
from . import location_bp
from app.extensions import db
from app.models import Location


@location_bp.route('/', methods=['POST'])
def create_location():
    data = request.get_json()

    if not data or not all(key in data for key in ['latitude', 'longitude']):
        return jsonify({'message': 'Missing required fields: latitude and longitude'}), 400

    new_location = Location(
        latitude=data['latitude'],
        longitude=data['longitude'],
        address=data.get('address', None),
        city=data.get('city', None),
        postal_code=data.get('postal_code', None)
    )

    db.session.add(new_location)
    db.session.commit()

    return jsonify({'message': 'Location created successfully', 'id': new_location.id}), 201


@location_bp.route('/', methods=['GET'])
def get_all_locations():
    locations = Location.query.all()

    if not locations:
        return jsonify({'message': 'No locations found'}), 404

    result = [
        {
            'id': location.id,
            'latitude': location.latitude,
            'longitude': location.longitude,
            'address': location.address,
            'city': location.city,
            'postal_code': location.postal_code
        }
        for location in locations
    ]

    return jsonify({'locations': result}), 200

@location_bp.route('/<int:id>', methods=['GET'])
def get_location(id):
    location = Location.query.get(id)

    if not location:
        return jsonify({'message': 'Location not found'}), 404

    result = {
        'id': location.id,
        'latitude': location.latitude,
        'longitude': location.longitude,
        'address': location.address,
        'city': location.city,
        'postal_code': location.postal_code
    }

    return jsonify(result), 200


@location_bp.route('/<int:id>', methods=['PUT'])
def update_location(id):
    location = Location.query.get(id)

    if not location:
        return jsonify({'message': 'Location not found'}), 404

    data = request.get_json()

    location.latitude = data.get('latitude', location.latitude)
    location.longitude = data.get('longitude', location.longitude)
    location.address = data.get('address', location.address)
    location.city = data.get('city', location.city)
    location.postal_code = data.get('postal_code', location.postal_code)

    db.session.commit()

    return jsonify({'message': 'Location updated successfully'}), 200


@location_bp.route('/<int:id>', methods=['DELETE'])
def delete_location(id):
    location = Location.query.get(id)

    if not location:
        return jsonify({'message': 'Location not found'}), 404

    db.session.delete(location)
    db.session.commit()

    return jsonify({'message': f'Location {id} deleted successfully'}), 200
