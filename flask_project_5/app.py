from flask import Flask
from models import db
from flask_jwt_extended import JWTManager, create_access_token

app = Flask(__name__)
app.config.from_object('config')
jwt = JWTManager(app)
db.init_app(app)

from views import *

if __name__ == '__main__':
    app.run()
