from main.settings import app
from flask import Blueprint
from . import views


app_house = Blueprint('house_apis', __name__)
app_house.add_url_rule('/house', 'house space', view_func=views.HouseSpaceView.as_view('house space'))
app_house.add_url_rule('/house/<int:post_id>/', 'house detail', view_func=views.HouseDetailView.as_view('house detail'))
