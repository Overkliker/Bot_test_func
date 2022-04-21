import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Spot(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'spots'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    lat = sqlalchemy.Column(sqlalchemy.REAL, nullable=True)
    lon = sqlalchemy.Column(sqlalchemy.REAL, nullable=True)
    photo = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user = orm.relation('User')
