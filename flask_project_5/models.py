from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    db.init_app(app)
    return app


events_cats = db.Table('events_cats',
                       db.Column('event_id', db.Integer, db.ForeignKey('events.id'), primary_key=True),
                       db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True))

events_types = db.Table('events_types',
                        db.Column('event_id', db.Integer, db.ForeignKey('events.id'), primary_key=True),
                        db.Column('type_id', db.Integer, db.ForeignKey('types.id'), primary_key=True))

events_locs = db.Table('events_locs',
                       db.Column('event_id', db.Integer, db.ForeignKey('events.id')),
                       db.Column('location_id', db.Integer, db.ForeignKey('locations.id')))

enrollments = db.Table('enrollments',
                       db.Column('event_id', db.Integer, db.ForeignKey('events.id')),
                       db.Column('participant_id', db.Integer, db.ForeignKey('participants.id')),
                       db.Column('datetime', db.DateTime(), default=datetime.now(), nullable=False))


# Таблица Event – События
class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(512), nullable=False)
    date = db.Column(db.DateTime(), nullable=False)
    time = db.Column(db.DateTime(), nullable=False)
    types = db.relationship('TypeEvent',
                            secondary=events_types,
                            lazy='subquery',
                            backref=db.backref('events', lazy=True))
    categories = db.relationship('Category',
                                 secondary=events_cats,
                                 lazy='subquery',
                                 backref=db.backref('events', lazy=True))
    locations = db.relationship('Location',
                                secondary=events_locs,
                                back_populates='events')
    address = db.Column(db.String(128), nullable=False)
    seats = db.Column(db.Integer(), nullable=False)
    participants = db.relationship('Participant',
                                   secondary=enrollments,
                                   backref='events',
                                   lazy=True)


# Таблица Participants – Участники
class Participant(db.Model):
    __tablename__ = 'participants'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    picture = db.Column(db.String(64000), nullable=False)
    location = db.Column(db.String(128), nullable=False)
    about = db.Column(db.String(512), nullable=False)

    @property
    def password(self):
        raise AttributeError("Вам не нужно знать пароль!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def password_valid(self, password):
        return check_password_hash(self.password_hash, password)


# Таблица Location – города
class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer(), primary_key=True)
    code = db.Column(db.String(16), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    events = db.relationship('Event',
                             secondary=events_locs,
                             back_populates='locations')


# Таблица Category – категории эвентов
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer(), primary_key=True)
    code = db.Column(db.String(16), nullable=False)
    title = db.Column(db.String(128), nullable=False)


# Таблица Type – типы эвентов
class TypeEvent(db.Model):
    __tablename__ = 'types'
    id = db.Column(db.Integer(), primary_key=True)
    code = db.Column(db.String(16), nullable=False)
    title = db.Column(db.String(128), nullable=False)
