from flask import request, jsonify
from . import delivery_bp
from app.extensions import db
from app.models import DeliveryAssignment, Publication, DeliveryPerson, Location
from datetime import datetime
from .optimizer import distribute_work

@delivery_bp.route('/', methods=['POST'])
def create_delivery_assignment():
    data = request.get_json()

    try:
        assignment_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid date format. Please use YYYY-MM-DD'}), 400

    new_assignment = DeliveryAssignment(
        date=assignment_date
    )

    new_assignment.locations = []

    # Add publications (many-to-many relationship)
    publication_ids = data.get('publication_ids', [])
    publications = Publication.query.filter(Publication.id.in_(publication_ids)).all()
    new_assignment.publications.extend(publications)

    location_ids = data.get("location_ids", [])
    locations = Location.query.filter(Location.id.in_(location_ids)).all()
    new_assignment.locations.extend(locations)

    # Add to the session and commit
    db.session.add(new_assignment)
    db.session.commit()

    return jsonify({'message': 'Delivery assignment created', 'id': new_assignment.id}), 201

@delivery_bp.route('/', methods=['GET'])
def get_delivery_assignments():
    delivery_person_id = request.args.get('delivery_person_id', type=int)
    date_str = request.args.get('date')

    query = DeliveryAssignment.query

    if delivery_person_id:
        query = query.filter(DeliveryAssignment.delivery_person_id == delivery_person_id)

    if date_str:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter(DeliveryAssignment.date == date_obj)
        except ValueError:
            return jsonify({'message': 'Invalid date format. Please use YYYY-MM-DD'}), 400

    assignments = query.all()

    if not assignments:
        return jsonify({'message': 'No delivery assignments found.'}), 404

    result = [
        {
            'id': assignment.id,
            'delivery_person_id': assignment.delivery_person_id,
            'date': assignment.date.isoformat(),
            'address': [location.address for location in assignment.locations],
            'publications': [publication.title for publication in assignment.publications]
        }
        for assignment in assignments
    ]

    return jsonify(result)



@delivery_bp.route('/<int:id>', methods=['GET'])
def get_delivery_assignment(id):
    assignment = DeliveryAssignment.query.get(id)

    if not assignment:
        return jsonify({'message': 'Delivery assignment not found'}), 404

    result = {
        'id': assignment.id,
        'delivery_person_id': assignment.delivery_person_id,
        'date': assignment.date.isoformat(),
        'locations': [location.address for location in assignment.locations],  # Addresses of locations
        'publications': [publication.title for publication in assignment.publications]
    }

    return jsonify(result)


@delivery_bp.route('/<int:id>', methods=['PUT'])
def update_delivery_assignment(id):
    assignment = DeliveryAssignment.query.get(id)

    if not assignment:
        return jsonify({'message': 'Delivery assignment not found'}), 404

    data = request.get_json()

    assignment.delivery_person_id = data.get('delivery_person_id', assignment.delivery_person_id)
    assignment.date = data.get('date', assignment.date)

    publication_ids = data.get('publication_ids', [])
    if publication_ids:
        publications = Publication.query.filter(Publication.id.in_(publication_ids)).all()
        assignment.publications = publications

    location_ids = data.get('location_ids', [])
    if location_ids:
        locations = Location.query.filter(Location.id.in_(location_ids)).all()
        assignment.locations = locations 

    db.session.commit()

    return jsonify({'message': 'Delivery assignment updated successfully'}), 200


@delivery_bp.route('/<int:id>', methods=['DELETE'])
def delete_delivery_assignment(id):
    assignment = DeliveryAssignment.query.get(id)

    if not assignment:
        return jsonify({'message': 'Delivery assignment not found'}), 404

    db.session.delete(assignment)
    db.session.commit()

    return jsonify({'message': f'Delivery assignment {id} deleted successfully'}), 200

@delivery_bp.route('/daily/<date>', methods=['GET'])
def get_daily_deliveries(date):
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid date format. Please use YYYY-MM-DD'}), 400

    delivery_person_id = request.args.get('delivery_person_id', type=int)  # optional filter

    deliveries = DeliveryAssignment.query.filter_by(date=date_obj)

    if delivery_person_id:
        deliveries = deliveries.filter(DeliveryAssignment.delivery_person_id == delivery_person_id)

    deliveries = deliveries.all()

    if not deliveries:
        return jsonify({'message': 'No deliveries found for the specified date'}), 404

    result = [
        {
            'id': delivery.id,
            'delivery_person_id': delivery.delivery_person_id,
            'locations': [d.address for d in delivery.locations],
            'publications': [pub.title for pub in delivery.publications]
        }
        for delivery in deliveries
    ]

    return jsonify({'deliveries': result}), 200


@delivery_bp.route('/person/<int:id>', methods=['GET'])
def get_person_deliveries(id):
    deliveries = DeliveryAssignment.query.filter_by(delivery_person_id=id).all()

    if not deliveries:
        return jsonify({'message': 'No deliveries found for this delivery person'}), 404

    result = [
        {
            'id': delivery.id,
            'date': delivery.date.strftime('%Y-%m-%d'),
            'locations': [d.address for d in delivery.locations],
            'publications': [pub.title for pub in delivery.publications]
        }
        for delivery in deliveries
    ]

    return jsonify({'deliveries': result}), 200

@delivery_bp.route('/assign/<date>', methods=['POST'])
def assign_deliveries(date):
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid date format. Please use YYYY-MM-DD'}), 400

    unassigned_deliveries = DeliveryAssignment.query.filter_by(date=date_obj, delivery_person_id=None).all()

    is_active = request.args.get('is_active', type=bool)
    if is_active is not None:
        delivery_persons = DeliveryPerson.query.filter_by(is_active=is_active).all()
        unassigned_deliveries = unassigned_deliveries.filter(DeliveryAssignment.delivery_person_id.in_([dp.id for dp in delivery_persons]))

    if not unassigned_deliveries:
        return jsonify({'message': 'No unassigned deliveries for the specified date'}), 404
    
    delivery_persons = DeliveryPerson.query.filter_by(is_active=True).all()
    if not delivery_persons:
        return jsonify({'message': 'No active delivery persons available for assignment'}), 400

    total_deliveries = len(unassigned_deliveries)
    total_carriers = len(delivery_persons)

    # more deliveries than carriers
    if total_deliveries > total_carriers:
        selected_carriers = delivery_persons 
        deliveries_per_carrier = total_deliveries // total_carriers
        remaining = total_deliveries % total_carriers
    else:
        selected_carriers = delivery_persons[:total_deliveries]
        deliveries_per_carrier = 1
        remaining = 0 
    
    # Distribute the work equally
    assignment_list = distribute_work(unassigned_deliveries, delivery_persons, deliveries_per_carrier, remaining)
    
    for carrier, deliveries in assignment_list:
        for delivery in deliveries:
            delivery.delivery_person_id = carrier.id
            db.session.add(delivery)

    db.session.commit()

    # Debug 
    for carrier, deliveries in assignment_list:
        print(f"Carrier {carrier.id} assigned deliveries: {[delivery.id for delivery in deliveries]}")

    return jsonify({'message': 'Deliveries assigned successfully'}), 200

