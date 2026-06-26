from flask import Blueprint
from flask import jsonify
from flask import request
from application.model.TrekModel import UserTable
# from application.controllers.user_controller import UserController

user_bp = Blueprint(
    "users",
    __name__,
    url_prefix="/users"
)
