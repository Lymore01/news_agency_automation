from .extensions import db
from datetime import datetime
from sqlalchemy import Index


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    phone = db.Column(db.String(200))
    subscriptions = db.relationship('Subscription', backref='customer_ref', cascade='all, delete')

    def __repr__(self):
        return f"<Customer {self.name}>"

class Publication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    type = db.Column(db.String(20))

    def __repr__(self):
        return f"<Publication {self.title}>"

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    publication_id = db.Column(db.Integer, db.ForeignKey('publication.id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date, nullable=True)

    customer = db.relationship('Customer', backref='customer_subscriptions', lazy=True)
    publication = db.relationship('Publication', backref='subscriptions', lazy=True)

    def __repr__(self):
        return f"<Subscription {self.publication_id} for Customer {self.customer_id}>"

    def is_active(self):
        """Return whether subscription is active"""
        return self.end_date is None or self.end_date >= datetime.today().date()

from app.extensions import db
from datetime import datetime

#! TODO: Fix alembic issue by naming all unique constraints
class DeliveryPerson(db.Model):
    __tablename__ = 'delivery_persons'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=True)
    vehicle_id = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    hire_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationship: a delivery person can have many delivery assignments
    # (This is the "one-to-many" relationship with DeliveryAssignments)
    assignments = db.relationship('DeliveryAssignment', backref='delivery_persons', lazy=True)

    def __repr__(self):
        return f"<DeliveryPerson {self.name}>"

    def get_assigned_deliveries(self):
        """Returns all delivery assignments for this delivery person"""
        return [assignment.id for assignment in self.assignments]
    
    def deactivate(self):
        """Deactivate this delivery person (set is_active to False)"""
        self.is_active = False
        db.session.commit()

    def activate(self):
        """Activate this delivery person (set is_active to True)"""
        self.is_active = True
        db.session.commit()


class DeliveryAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    delivery_person_id = db.Column(
    db.Integer,
    db.ForeignKey('delivery_persons.id', name='fk_delivery_assignment_delivery_person')
)
    date = db.Column(db.Date)
    address = db.Column(db.String(200))
    
    delivery_person = db.relationship('DeliveryPerson', backref='assignments')
    publications = db.relationship('Publication', secondary='delivery_assignment_publication', backref='assignments')

    def __repr__(self):
        return f"<DeliveryAssignment {self.date} at {self.address}>"

class DeliveryAssignmentPublication(db.Model):
    __tablename__ = 'delivery_assignment_publication'
    id = db.Column(db.Integer, primary_key=True)
    delivery_assignment_id = db.Column(db.Integer, db.ForeignKey('delivery_assignment.id'))
    publication_id = db.Column(
    db.Integer,
    db.ForeignKey('publication.id', name='fk_delivery_assignment_pub_publication')
)

    delivery_assignment = db.relationship('DeliveryAssignment', backref='delivery_publications')
    publication = db.relationship('Publication', backref='delivery_assignments')