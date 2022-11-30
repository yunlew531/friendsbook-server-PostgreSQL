from config.db import BASE
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from time import time
from model.user import User

class Friend(BASE):
  __tablename__ = 'friends'

  id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
  usera_uid = Column(String(36), ForeignKey('users.uid'))
  userb_uid = Column(String(36), ForeignKey('users.uid'))
  connected_time = Column(Float)
  invited_time = Column(Float, default=time)
  connected = Column(Boolean, default=False)

  usera = relationship(User, foreign_keys=usera_uid)
  userb = relationship(User, foreign_keys=userb_uid)

