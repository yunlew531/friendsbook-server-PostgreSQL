from config.db import BASE
import sqlalchemy as sa

class User(BASE):
  __tablename__ = 'users'

  id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
  name = sa.Column(sa.String(20), nullable=False)
  nickname = sa.Column(sa.String(20))
  age = sa.Column(sa.Integer)

  def get_name(self):
    return self.name
