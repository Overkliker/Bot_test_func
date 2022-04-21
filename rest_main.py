from data import db_session
from data.user import User
import spots_api
from data.spots import Spot
from flask import Flask
import flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


if __name__ == '__main__':
    db_session.global_init("data/tg_bot.db")
    app.register_blueprint(spots_api.spots_blueprint)
    app.run()
