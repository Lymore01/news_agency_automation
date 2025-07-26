from flask import Flask
from .extensions import db, migrate
from .customer import customer_bp
from .subscription import subscription_bp
from .publication import publication_bp
from .delivery import delivery_bp
from .carrier import carrier_bp
from .location import location_bp
from .auth import auth_bp
from flask_login import LoginManager
from flask import jsonify
from .models import User

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    login_manager.init_app(app)

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({'message': 'Unauthorized access'}), 401

    # initialize extensions
    db.init_app(app)
    migrate.init_app(app, db) 

    # register blueprints
    app.register_blueprint(customer_bp)
    app.register_blueprint(subscription_bp)
    app.register_blueprint(publication_bp)
    app.register_blueprint(delivery_bp)
    app.register_blueprint(carrier_bp)
    app.register_blueprint(location_bp)
    app.register_blueprint(auth_bp)

    with app.app_context():
        db.create_all()
    return app