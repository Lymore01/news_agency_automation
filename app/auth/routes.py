from flask import jsonify, request
from . import auth_bp
from app.extensions import db
from app.models import User
from .utils import hash_password, check_password
from flask_login import login_user, logout_user, login_required

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not all(key in data for key in ['email', 'password']):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # check if user already exists
    existing_email = User.query.filter_by(email=data['email']).first()
    if existing_email:
        return jsonify({'message': 'Email already registered'}), 400
    
    username = data.get('username', None)
    
    hashed_password = hash_password(data['password'])
    new_user = User(
        username=username,
        email=data['email'],
        password=hashed_password
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            'message': 'User registered successfully',
            'user': {
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email}
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f"An error occurred: {str(e)}"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    print(f"Login attempt for user: {user}")
    if user.email == email and check_password(password, user.password):
        login_user(user)
        return jsonify({'message': 'Logged in successfully'}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200