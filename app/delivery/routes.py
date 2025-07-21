from flask import request, jsonify
from . import delivery_bp
from app.extensions import db
from app.models import DeliveryAssignment, Publication

@delivery_bp.route('/', methods=['POST'])
def create_delivery_assignment():
    data = request.get_json()

    new_assignment = DeliveryAssignment(
        delivery_person_id=data['delivery_person_id'],
        date=data['date'],
        address=data['address']
    )

    # Add publications (many-to-many relationship)
    publication_ids = data.get('publication_ids', [])
    publications = Publication.query.filter(Publication.id.in_(publication_ids)).all()
    new_assignment.publications.extend(publications)

    # Add to the session and commit
    db.session.add(new_assignment)
    db.session.commit()

    return jsonify({'message': 'Delivery assignment created', 'id': new_assignment.id}), 201

@delivery_bp.route('/', methods=['GET'])
def get_delivery_assignments():
    assignments = DeliveryAssignment.query.all()

    if not assignments:
        return jsonify({'message': 'No delivery assignments found.'}), 404

    result = [
        {
            'id': assignment.id,
            'delivery_person_id': assignment.delivery_person_id,
            'date': assignment.date.isoformat(),
            'address': assignment.address,
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
        'address': assignment.address,
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
    assignment.address = data.get('address', assignment.address)

    # Update publications (if passed)
    publication_ids = data.get('publication_ids', [])
    if publication_ids:
        publications = Publication.query.filter(Publication.id.in_(publication_ids)).all()
        assignment.publications = publications

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
