from config.db import BASE
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from time import time

class Article(BASE):
  __tablename__ = 'articles'

  id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
  content = Column(String, nullable=False)
  created_at = Column(Float, default=time)

  # indicates who can see the article. 1 = all, 2 = friend, 3 = owner
  access = Column(Integer, default=1)

  user_uid = Column(String(36), ForeignKey('users.uid'))

  comments = relationship('Comment')
  thumbs_up = relationship('ArticleThumbsUp')

class Comment(BASE):
  __tablename__ = 'comments'

  id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
  content = Column(String(300), nullable=False)
  created_at = Column(Float, default=time)
  article_id = Column(Integer, ForeignKey('articles.id'))
  user_uid = Column(String(36), ForeignKey('users.uid'))

class ArticleThumbsUp(BASE):
  __tablename__ = 'thumbs_up'

  id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
  user_uid = Column(String(36), ForeignKey('users.uid'))
  article_id = Column(Integer, ForeignKey('articles.id'))
  created_at = Column(Float, default=time)