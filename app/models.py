from .extensions import db
from datetime import datetime
from sqlalchemy import Index


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    phone = db.Column(db.String(200), unique=True)
    subscriptions = db.relationship('Subscription', backref='customer_ref', cascade='all, delete')

    def __repr__(self):
        return f"<Customer {self.name}>"

class Publication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    type = db.Column(db.String(20))
    subscriptions = db.relationship('Subscription', back_populates='publication')

    def __repr__(self):
        return f"<Publication {self.title}>"

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    publication_id = db.Column(db.Integer, db.ForeignKey('publication.id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), nullable=False, default="pending") 
    requested_change_date = db.Column(db.Date, nullable=True)
    change_approved = db.Column(db.Boolean, default=False)

    customer = db.relationship('Customer', backref='customer_subscriptions', lazy=True)
    publication = db.relationship('Publication', backref='subscriptions_', lazy=True)

    def __repr__(self):
        return f"<Subscription {self.publication_id} for Customer {self.customer_id}>"

    def is_active(self):
        """Return whether subscription is active"""
        return self.end_date is None or self.end_date >= datetime.today().date()

class DeliveryPerson(db.Model):
    __tablename__ = 'delivery_persons'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=True)
    vehicle_id = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    hire_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    latitude = db.Column(db.Float, nullable=False, default=0.0)  
    longitude = db.Column(db.Float, nullable=False, default=0.0) 

    # Relationship: a delivery person can have many delivery assignments
    # (This is the "one-to-many" relationship with DeliveryAssignments)
    assignments = db.relationship('DeliveryAssignment', backref='delivery_person', lazy=True)

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

delivery_assignment_location = db.Table('delivery_assignment_location',
    db.Column('delivery_assignment_id', db.Integer, db.ForeignKey('delivery_assignment.id'), primary_key=True),
    db.Column('location_id', db.Integer, db.ForeignKey('locations.id'), primary_key=True)
)

class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)

    delivery_assignments = db.relationship('DeliveryAssignment', secondary=delivery_assignment_location, backref='locations_')

    def __repr__(self):
        return f"<Location {self.city} - {self.address}>"

class DeliveryAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    delivery_person_id = db.Column(
    db.Integer,
    db.ForeignKey('delivery_persons.id', name='fk_delivery_assignment_delivery_persons')
)
    date = db.Column(db.Date)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id', name='fk_delivery_assignments_location'))
   
    locations = db.relationship('Location', secondary=delivery_assignment_location, backref='delivery_assignment')
    carrier = db.relationship('DeliveryPerson', backref='delivery_person_assignments')
    publications = db.relationship('Publication', secondary='delivery_assignment_publication', backref='assignments')

    def __repr__(self):
        return f"<DeliveryAssignment {self.date} at {self.locations}>"

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