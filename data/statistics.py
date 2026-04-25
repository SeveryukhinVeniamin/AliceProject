import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Statistics(SqlAlchemyBase):
    __tablename__ = 'statistics'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    url = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    picture_id = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    full_name_place = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
