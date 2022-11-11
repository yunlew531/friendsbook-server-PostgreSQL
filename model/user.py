from config.db import BASE
from sqlalchemy import Column, Integer, String, TIMESTAMP
from datetime import datetime

class User(BASE):
  __tablename__ = 'users'

  id = Column(Integer, primary_key=True, autoincrement=True)
  name = Column(String(20), nullable=False)
  nickname = Column(String(20))
  email = Column(String(120))
  password = Column(String(30))
  age = Column(Integer)
  created_at = Column(TIMESTAMP, default=datetime.now)

  def get_name(self):
    return self.name