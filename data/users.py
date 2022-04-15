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
    mistakes_0 = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    mistakes_1 = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    mistakes_2 = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    mistakes_3 = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    mistakes_4 = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    total_grade = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    def find_worst(self):
        find_dict = {"Квадратные уравнения": self.mistakes_0, "Расчетные задачи": self.mistakes_1,
                     "Прогрессии": self.mistakes_2, "Геометрия": self.mistakes_3,
                     "Теория вероятности": self.mistakes_4}
        return sorted(find_dict, key=find_dict.get, reverse=True)[0]