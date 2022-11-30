from config.db import BASE
from sqlalchemy import Column, Integer, String, Float, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from time import time

class Chatroom(BASE):
  __tablename__ = 'chatrooms'

  id = Column(Integer, primary_key=True)
  name = Column(String(10))
  members = Column(ARRAY(String(36)), nullable=False)
  created_at = Column(Float, default=time)
  type = Column(Integer, nullable=False) # 1 = one to one, 2 = multiple

  chats = relationship('Chat')

class Chat(BASE):
  __tablename__ = 'chats'

  id = Column(Integer, primary_key=True)
  chatroom_id = Column(Integer, ForeignKey('chatrooms.id'))
  user_uid = Column(String(36), ForeignKey('users.uid'))
  content = Column(String(300), nullable=False)
  created_at = Column(Float, default=time)
  status = Column(Integer, default=1) # 1 = normal, 2 = delete
  read_user = Column(ARRAY(String(36)))