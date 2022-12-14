from config.db import BASE
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.dialects.postgresql import ARRAY
from uuid import uuid4
from time import time
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableList
from model.chat import Chat

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
  city = Column(String(10))
  alternate_email = Column(MutableList.as_mutable(ARRAY(String(120))))
  created_at = Column(Float, default=time)
  last_seen = Column(Float)
  banner_url = Column(String)
  avatar_url = Column(String)

  articles = relationship('Article')
  comments = relationship('Comment')
  article_likes = relationship('ArticleLike')
  images = relationship('Image')
  chats = relationship('Chat')

  def get_name(self):
    return self.name