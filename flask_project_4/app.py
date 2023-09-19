from flask import Flask
from models import db
from flask_migrate import Migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    db.init_app(app)
    return app


app = create_app()
migrate = Migrate(app, db)

from views import *


def format_datetime(value, format="%d %m"):
    months = {'01': 'Января',
              '02': 'Февраля',
              '03': 'Марта',
              '04': 'Апреля',
              '05': 'Мая',
              '06': 'Июня',
              '07': 'Июля',
              '08': 'Августа',
              '09': 'Сентября',
              '10': 'Октября',
              '11': 'Ноября',
              '12': 'Декабря'}
    if value is None:
        return ""
    date, month = value.strftime(format).split()
    value = date + " " + months[month]
    return value


# регистрируем новый фильтр для использовании в Jinja
app.jinja_env.filters['formatdatetime'] = format_datetime

if __name__ == '__main__':
    app.run()
