from flask import request, jsonify
from . import subscription_bp
from app.extensions import db
from app.models import Subscription, Customer, Publication
from datetime import datetime

@subscription_bp.route('/', methods=['GET'])
def get_subscriptions():
    subscriptions = Subscription.query.all()

    if not subscriptions:
        return jsonify({'message': 'No subscriptions found.'}), 404

    result = [
        {
            'id': s.id,
            'customer_id': s.customer_id,
            'customer_name': s.customer.name,
            'publication_id': s.publication_id,
            'publication_name': s.publication.name,
            'start_date': s.start_date.isoformat(),
            'end_date': s.end_date.isoformat() if s.end_date else None,
            'status': 'active' if s.is_active() else 'expired'
        }
        for s in subscriptions
    ]

    return jsonify(result)

@subscription_bp.route('/', methods=['POST'])
def create_subscription():
    data = request.get_json()

    if not data or not all(key in data for key in ['customer_id', 'publication_id', 'start_date']):
        return jsonify({'message': 'Missing required fields'}), 400

    customer = Customer.query.get(data['customer_id'])
    publication = Publication.query.get(data['publication_id'])

    if not customer:
        return jsonify({'message': 'Customer not found'}), 404
    
    if not publication:
        return jsonify({'message': 'Publication not found'}), 404
    
    new_subscription = Subscription(
        customer_id=data['customer_id'],
        publication_id=data['publication_id'],
        start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
        end_date=None 
    )

    # Add to the session and commit to the database
    try:
        db.session.add(new_subscription)
        db.session.commit()
        return jsonify({
            'id': new_subscription.id,
            'customer_id': new_subscription.customer_id,
            'publication_id': new_subscription.publication_id,
            'start_date': new_subscription.start_date.isoformat(),
            'status': 'active'
        }), 201
    except Exception as e:
        db.session.rollback() 
        return jsonify({'message': str(e)}), 500

@subscription_bp.route('/<int:id>', methods=['GET'])
def get_subscription_by_id(id):
    subscription = Subscription.query.get(id)

    if not subscription:
        return jsonify({'message': 'Subscription not found'}), 404

    result = {
        'id': subscription.id,
        'customer_id': subscription.customer_id,
        'customer_name': subscription.customer.name,
        'publication_id': subscription.publication_id,
        'publication_name': subscription.publication.title,
        'start_date': subscription.start_date.isoformat(),
        'end_date': subscription.end_date.isoformat() if subscription.end_date else None,
        'status': 'active' if subscription.is_active() else 'expired'
    }

    return jsonify(result)


@subscription_bp.route('/<int:id>', methods=['PUT'])
def update_subscription(id):
    subscription = Subscription.query.get(id)

    if not subscription:
        return jsonify({'message': 'Subscription not found'}), 404

    data = request.get_json()

    if 'end_date' in data:
        try:
            subscription.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            db.session.commit()
            return jsonify({
                'id': subscription.id,
                'customer_id': subscription.customer_id,
                'publication_id': subscription.publication_id,
                'start_date': subscription.start_date.isoformat(),
                'end_date': subscription.end_date.isoformat(),
                'status': 'expired' if subscription.end_date else 'active'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': str(e)}), 500

    return jsonify({'message': 'No update field found'}), 400


@subscription_bp.route('/<int:id>', methods=['DELETE'])
def delete_subscription(id):
    subscription = Subscription.query.get(id)

    if not subscription:
        return jsonify({'message': 'Subscription not found'}), 404

    try:
        db.session.delete(subscription)
        db.session.commit()
        return jsonify({'message': 'Subscription deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500
