from config.db import BASE
from sqlalchemy import Column, Integer, String, Float
from uuid import uuid4
from time import time
from sqlalchemy.orm import relationship

def create_uuid():
  return str(uuid4())

class User(BASE):
  __tablename__ = 'users'

  uid = Column(String(36), primary_key=True, unique=True, default=create_uuid)
  name = Column(String(20), nullable=False)
  nickname = Column(String(20))
  email = Column(String(120))
  password = Column(String(30))
  age = Column(Integer)
  created_at = Column(Float, default=time)
  last_seen = Column(Float)
  banner_url = Column(String)
  avatar_url = Column(String)

  articles = relationship('Article')
  comments = relationship('Comment')
  thumbs_up = relationship('ArticleThumbsUp')
  images = relationship('Image')

  def get_name(self):
    return self.name