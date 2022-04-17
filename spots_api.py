from flask import Blueprint, jsonify, make_response, request
from data import db_session
from data.spots import Spot

spots_blueprint = Blueprint(
    'spots_api',
    __name__
)

