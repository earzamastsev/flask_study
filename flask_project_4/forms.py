from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, HiddenField, IntegerField
from wtforms.validators import Email, Length, Regexp


class LoginForm(FlaskForm):
    email = StringField('Электропочта', validators=[Email(message='Не похоже на адрес электронной почты.')])
    password = PasswordField('Пароль')


class RegisterForm(FlaskForm):
    name = StringField('Ваше имя',
                       validators=[Length(min=2,
                                          message='Адрес не должен быть менее 2 символов.')])
    email = StringField('Электропочта',
                        validators=[Email(message='Не похоже на адрес электронной почты.')])
    password = PasswordField('Пароль',
                             validators=[Length(min=5,
                                                message='Пароль должен быть не менее 5 символов.')])
    address = StringField('Адрес доставки заказов',
                          validators=[Length(min=10,
                                             message='Адрес не должен быть менее 10 символов.')])
    phone = StringField('Телефон (в формате 79122233444)',
                        validators=[Length(min=11,
                                           message='Не похоже на телефонный номер.')])


class OrderForm(FlaskForm):
    name = StringField('Ваше имя',
                       validators=[Length(min=2,
                                          message='Адрес не должен быть менее 2 символов.')])
    address = StringField('Адрес доставки заказов',
                          validators=[Length(min=10,
                                             message='Адрес не должен быть менее 10 символов.')])
    email = StringField('Электропочта', validators=[Email(message='Не похоже на адрес электронной почты.')])
    phone = StringField('Телефон (в формате 79122233444)',
                        validators=[Length(min=11,
                                           message='Не похоже на телефонный номер.')])
    meals = HiddenField()
    summa = HiddenField()
    user = HiddenField()
