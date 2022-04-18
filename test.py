from data import db_session
from data.spots import Spot
from data.user import User
from help_defs import compute_delta, around


db_session.global_init("data/tg_bot.db")
session = db_session.create_session()
spots = session.query(User.lat, User.lon).filter(User.id == 785760784).one()
print(type(spots[0]))
print(type(3.3))
lat = compute_delta(spots[0])
lon = compute_delta(spots[1])
print(lat, lon)

around_lat = around(lat)
around_lon = around(lon)
print(around_lat, around_lon)

bet_lat1 = spots[0] - around_lat
print(bet_lat1)
bet_lat2 = spots[0] + around_lat

bet_lon1 = spots[1] - around_lon
print(bet_lat1)
bet_lon2 = spots[1] + around_lon

good_cords = session.query(Spot).filter(Spot.lat.between(bet_lat1, bet_lat2), Spot.lon.between(bet_lon1, bet_lon2)).all()
#
print(good_cords)