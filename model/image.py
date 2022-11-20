from config.db import BASE
from sqlalchemy import Column, String, Float, ForeignKey
from time import time

class Image(BASE):
  __tablename__ = 'images'

  id = Column(String(36), primary_key=True, nullable=False)
  url = Column(String, nullable=False)
  created_at = Column(Float, default=time)

  user_uid = Column(String(36), ForeignKey('users.uid'))
