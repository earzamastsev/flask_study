from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

db = SQLAlchemy()

meals_orders_association = db.Table('meals_orders', \
                                    db.Column('meal_id', db.Integer, db.ForeignKey('meals.id')), \
                                    db.Column('order_id', db.Integer, db.ForeignKey('orders.id'))
                                    )


class MealModel(db.Model):
    __tablename__ = 'meals'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1024), nullable=False)
    picture = db.Column(db.String(128), nullable=False)
    category = db.relationship('CategoryModel', back_populates='meals')
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    orders = db.relationship('OrderModel', secondary=meals_orders_association, back_populates='meals')


class CategoryModel(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    meals = db.relationship('MealModel', back_populates='category')


class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=True)
    name = role = db.Column(db.String(32), nullable=False, default='Аноним')
    address = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(32), nullable=False, default='guest')
    orders = db.relationship('OrderModel', back_populates='users')
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)

    @property
    def password(self):
        # Запретим прямое обращение к паролю
        raise AttributeError("Вам не нужно знать пароль!")

    @password.setter
    def password(self, password):
        # Устанавливаем пароль через этот метод
        self.password_hash = generate_password_hash(password)

    def password_valid(self, password):
        # Проверяем пароль через этот метод
        # Функция check_password_hash превращает password в хеш и сравнивает с хранимым
        return check_password_hash(self.password_hash, password)


class OrderModel(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.datetime.now)
    summa = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(128), default='Выполняется')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    users = db.relationship('UserModel', back_populates='orders')
    meals = db.relationship('MealModel', secondary=meals_orders_association, back_populates='orders')
