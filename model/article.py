from config.db import BASE
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from time import time

class Article(BASE):
  __tablename__ = 'articles'

  id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
  content = Column(String, nullable=False)
  published_at = Column(Float, default=time)

  # thumbs_up = EmbeddedDocumentListField(ThumbsUp, default=[])
  user_uid = Column(String(128), ForeignKey('users.uid'))
