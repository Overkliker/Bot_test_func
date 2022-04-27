import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Like(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'likes'

    # point_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('spots.id'), nullable=True)
    # user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    association_table = sqlalchemy.Table(
        'association',
        SqlAlchemyBase.metadata,
        sqlalchemy.Column('news', sqlalchemy.Integer,
                          sqlalchemy.ForeignKey('news.id')),
        sqlalchemy.Column('category', sqlalchemy.Integer,
                          sqlalchemy.ForeignKey('category.id'))
    )

    categories = orm.relation("Category",
                              secondary="association",
                              backref="news")

    user = orm.relation('User')
    spot = orm.relation('Spot')