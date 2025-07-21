from flask import request, jsonify
from . import customer_bp
from app.extensions import db
from app.models import Customer

@customer_bp.route('/', methods=['GET'])
def get_customers():
    try:
        customers = Customer.query.all()

        if not customers:
            return jsonify({'message': 'No customers found.'}), 200
        
        return jsonify([
            {
                'id': c.id,
                'name': c.name,
                'address': c.address,
                'phone': c.phone
            }
            for c in customers
        ])
    except Exception as e:
        return jsonify({'message': f"An error occurred: {str(e)}"}), 500

@customer_bp.route('/<int:id>', methods=['GET'])
def get_customer(id):
    try:
        customer = Customer.query.get(id)
        if not customer:
            return jsonify({'message': 'Customer not found'}), 404

        return jsonify({
            'id': customer.id,
            'name': customer.name,
            'address': customer.address,
            'phone': customer.phone
        })
    except Exception as e:
        return jsonify({'message': f"An error occurred: {str(e)}"}), 500

@customer_bp.route('/', methods=['POST'])
def create_customer():
    try:
        data = request.get_json()

        if not data or 'name' not in data or 'address' not in data:
            return jsonify({'message': 'Name and address are required fields.'}), 400

        # create new instance of the customer model
        new_customer = Customer(
            name=data['name'],
            address=data['address'],
            phone=data.get('phone')
        )

        # add a new object (Customer) to the session (staging area in memory)
        db.session.add(new_customer)

        # execute all staged operations, if success; store to the db permanently
        db.session.commit()
        return jsonify({'message': 'Customer added', 'id': new_customer.id}), 201
    except KeyError as e:
        return jsonify({'message': f'Missing field: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'message': f"An error occurred: {str(e)}"}), 500

@customer_bp.route('/<int:id>', methods=['PUT'])
def update_customer(id):
    try:
        customer = Customer.query.get(id)

        if not customer:
            return jsonify({'message': 'Customer not found'}), 404

        data = request.get_json()

        # update only the field sent for update, use the customer.<value> as the fallback
        customer.name = data.get('name', customer.name)
        customer.address = data.get('address', customer.address)
        customer.phone = data.get('phone', customer.phone)

        db.session.commit()

        return jsonify({
            'message': 'Customer updated successfully',
            'customer': {
                'id': customer.id,
                'name': customer.name,
                'address': customer.address,
                'phone': customer.phone
            }
        }), 200
    except KeyError as e:
        return jsonify({'message': f'Missing field: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'message': f"An error occurred: {str(e)}"}), 500

@customer_bp.route('/<int:id>', methods=['DELETE'])
def delete_customer(id):
    try:
        customer = Customer.query.get(id)

        if not customer:
            return jsonify({'message': 'Customer not found'}), 404

        db.session.delete(customer)
        db.session.commit()

        return jsonify({'message': f'Customer with ID {id} has been deleted.'}), 200
    except Exception as e:
        return jsonify({'message': f"An error occurred: {str(e)}"}), 500
