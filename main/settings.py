from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flasgger import Swagger
from flask import Flask
from dotenv import load_dotenv
from pathlib import Path
import os
load_dotenv()


app = Flask('app')
app.config['DEBUG'] = os.environ.get('DEBUG')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')


swagger = Swagger(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
