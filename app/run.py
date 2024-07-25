from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import Config


app = Flask(__name__)
app.config.from_object(Config())  # Load configuration

# Initialize the DB
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Register controllers
from controllers import api
app.register_blueprint(api, url_prefix='/api')

# for rule in app.url_map.iter_rules():
#     print(rule.rule, rule.endpoint)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=6699)
