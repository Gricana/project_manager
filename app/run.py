from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from app import Config
from views import api


app = Flask(__name__)
app.config.from_object(Config())

# URL register
app.register_blueprint(api, url_prefix='/api')

# Databases init
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import models

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5500)
