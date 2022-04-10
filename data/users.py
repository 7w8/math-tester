import datetime
import sqlalchemy
from flask_login import UserMixin

from data.db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    done_count = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    mistakes_count = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    total_grade = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
