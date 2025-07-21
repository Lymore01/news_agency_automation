from flask import Flask
from .extensions import db, migrate
from .customer import customer_bp
from .subscription import subscription_bp
from .publication import publication_bp
from .delivery import delivery_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # initialize extensions
    db.init_app(app)
    migrate.init_app(app, db) 

    # register blueprints
    app.register_blueprint(customer_bp)
    app.register_blueprint(subscription_bp)
    app.register_blueprint(publication_bp)
    app.register_blueprint(delivery_bp)

    with app.app_context():
        db.create_all()
    return app