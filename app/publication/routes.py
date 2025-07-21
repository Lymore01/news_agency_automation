from flask import request, jsonify
from app import db
from app.models import Publication
from . import publication_bp

@publication_bp.route('/', methods=['GET'])
def get_publications():
    publications = Publication.query.all()

    if not publications:
        return jsonify({'message': 'No publications found.'}), 404

    result = [
        {
            'id': p.id,
            'title': p.title,
            'type': p.type
        }
        for p in publications
    ]
    
    return jsonify(result)


@publication_bp.route('/', methods=['POST'])
def create_publication():
    data = request.get_json()

    if not data or not all(key in data for key in ['title', 'type']):
        return jsonify({'message': 'Missing required fields'}), 400

    if data['type'] not in ['newspaper', 'magazine']:
        return jsonify({'message': 'Invalid publication type. Must be "newspaper" or "magazine".'}), 400

    new_publication = Publication(
        title=data['title'],
        type=data['type']
    )

    try:
        db.session.add(new_publication)
        db.session.commit()
        return jsonify({
            'id': new_publication.id,
            'title': new_publication.title,
            'type': new_publication.type
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@publication_bp.route('/<int:id>', methods=['GET'])
def get_publication_by_id(id):
    publication = Publication.query.get(id)

    if not publication:
        return jsonify({'message': 'Publication not found'}), 404

    result = {
        'id': publication.id,
        'title': publication.title,
        'type': publication.type
    }

    return jsonify(result)


@publication_bp.route('/<int:id>', methods=['PUT'])
def update_publication(id):
    publication = Publication.query.get(id)

    if not publication:
        return jsonify({'message': 'Publication not found'}), 404

    data = request.get_json()

    if 'title' in data:
        publication.title = data['title']
    
    if 'type' in data:
        if data['type'] not in ['newspaper', 'magazine']:
            return jsonify({'message': 'Invalid publication type. Must be "newspaper" or "magazine".'}), 400
        publication.type = data['type']

    try:
        db.session.commit()
        return jsonify({
            'id': publication.id,
            'title': publication.title,
            'type': publication.type
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@publication_bp.route('/<int:id>', methods=['DELETE'])
def delete_publication(id):
    publication = Publication.query.get(id)

    if not publication:
        return jsonify({'message': 'Publication not found'}), 404

    try:
        db.session.delete(publication)
        db.session.commit()
        return jsonify({'message': 'Publication deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500
