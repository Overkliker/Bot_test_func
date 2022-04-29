from flask import Blueprint, jsonify, make_response, request
from data import db_session
from data.spots import Spot
from data.user import User
from help_defs import compute_delta, around

spots_blueprint = Blueprint(
    'spots_api',
    __name__
)
db_session.global_init("data/tg_bot.db")

@spots_blueprint.route('/api/get_spots/<int:user_id>', methods=['GET'])
def return_spots(user_id):

    session = db_session.create_session()
    spots = session.query(User.lat, User.lon).filter(User.id == user_id).one()
    lat = compute_delta(spots[0])
    lon = compute_delta(spots[1])

    around_lat = around(lat)
    around_lon = around(lon)

    bet_lat1 = spots[0] - around_lat
    bet_lat2 = spots[0] + around_lat

    bet_lon1 = spots[1] - around_lon
    bet_lon2 = spots[1] + around_lon

    good_cords = session.query(Spot).filter((Spot.lat.between(bet_lat1, bet_lat2)),
                                            (Spot.lon.between(bet_lon1, bet_lon2)))

    return jsonify(
        {
            'spots':
                [item.to_dict()
                 for item in good_cords],
            'delta_lat': around_lat,
            'delta_lon': around_lon
        }
    )


@spots_blueprint.route('/users/select/<id_>/cords')
def select_one_user_cords_(id_):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id_)
    return jsonify(
        {
            'user':
                [item.to_dict(only=('lat', 'lon'))
                 for item in user]
        }
    )