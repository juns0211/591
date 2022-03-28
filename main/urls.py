from flask_swagger import swagger
from flask import jsonify

from .settings import app


@app.route("/spec")
def spec():
    return jsonify(swagger(app))


from house.urls import app_house
app.register_blueprint(app_house, url_prefix='/api')
