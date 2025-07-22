from flask import request, jsonify
from . import subscription_bp
from app.extensions import db
from app.models import Subscription
from datetime import datetime, timedelta

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
            'publication_name': s.publication.title,
            'start_date': s.start_date.isoformat() if s.start_date else None,
            'end_date': s.end_date.isoformat() if s.end_date is not None else None,
            'status': s.status,
            'requested_change_date': s.requested_change_date,
            'change_approved': s.change_approved
        }
        for s in subscriptions
    ]

    return jsonify(result)

# subscribe
@subscription_bp.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json()

    customer_id = data['customer_id']
    publication_id = data['publication_id']

    subscription = Subscription.query.filter_by(customer_id=customer_id, publication_id=publication_id).first()
    
    if not customer_id or not publication_id:
        return jsonify({'message': 'Customer ID and Publication ID are required.'}), 400


    if subscription and (subscription.status == 'subscribed' or subscription.status == 'pending'):
        return jsonify({'message': 'User is already subscribed to this publication or the subscription is pending'}), 400


    new_subscription = Subscription(
        customer_id=customer_id,
        publication_id=publication_id,
        status='pending',
        requested_change_date=datetime.now().date()  # current date
    )

    db.session.add(new_subscription)
    db.session.commit()

    return jsonify({'message': 'Subscription request submitted. Change will be effective in 1 week.'}), 201

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
        'start_date': subscription.start_date.isoformat() if subscription.start_date is not None else None,
        'end_date': subscription.end_date.isoformat() if subscription.end_date is not None else None,
        'status': subscription.status,
        'requested_change_date': subscription.requested_change_date,
        'change_approved': subscription.change_approved
    }

    return jsonify(result)

# TODO: remove me
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
                'status': subscription.status,
                'requested_change_date': subscription.requested_change_date,
                'change_approved': subscription.change_approved
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': str(e)}), 500

    return jsonify({'message': 'No update field found'}), 400


# unsubscribe
@subscription_bp.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    data = request.get_json()

    customer_id = data['customer_id']
    publication_id = data['publication_id']

    subscription = Subscription.query.filter_by(customer_id=customer_id, publication_id=publication_id, status="subscribed").first()

    if not subscription:
        return jsonify({'message': 'User is not subscribed to this publication or subscription is still pending'}), 404

    if subscription.status == 'unsubscribed':
        return jsonify({'message': 'User is already unsubscribed from this publication'}), 400

    requested_change_date = subscription.requested_change_date
    current_date = datetime.utcnow().date()

    if (current_date - requested_change_date) < timedelta(weeks=1):
        return jsonify({'message': 'You must provide at least one week’s notice for unsubscribing.'}), 400

    subscription.status = 'unsubscribed'
    subscription.change_approved = True 

    db.session.commit()

    return jsonify({'message': 'Unsubscription request confirmed. You will be unsubscribed after 1 week.'}), 200

# force delete - only admins
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
