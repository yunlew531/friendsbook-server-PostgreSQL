from config.db import BASE
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from model.user import User
from time import time

class Notification(BASE):
  __tablename__ = 'notifications'

  id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
  user_uid = Column(String(36), ForeignKey('users.uid'), nullable=False)
  invited_from = Column(String(36), ForeignKey('users.uid'))
  type = Column(Integer, nullable=False)  #  '1 = friend invited, 2 = user article tag, 3 = group invited, 4 = group article new post'
  read = Column(Boolean, default=False)
  article_id = Column(Integer, ForeignKey('articles.id'))
  # group_id = Column(Integer, ForeignKey('groups.id'))
  created_at = Column(Float, default=time)

  user = relationship(User, foreign_keys=user_uid)
  invited_user_from = relationship(User, foreign_keys=invited_from)

