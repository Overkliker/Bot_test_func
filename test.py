from data.spots import Spot
from data.user import User
from help_defs import compute_delta, around
from data import db_session
from flask import jsonify


db_session.global_init("data/tg_bot.db")
session = db_session.create_session()
spots = session.query(User.lat, User.lon).filter(User.id == 785760784).one()
lat = compute_delta(spots[0])
lon = compute_delta(spots[1])

around_lat = around(lat)
around_lon = around(lon)

bet_lat1 = spots[0] - around_lat
bet_lat2 = spots[0] + around_lat

bet_lon1 = spots[1] - around_lon
bet_lon2 = spots[1] + around_lon


good_cords = session.query(Spot).filter((Spot.lat.between(bet_lat1, bet_lat2)), (Spot.lon.between(bet_lon1, bet_lon2)))

l1 = []
for i in good_cords:
    print(i.to_dict())

