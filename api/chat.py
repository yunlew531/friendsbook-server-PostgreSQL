from flask import g
from flask_restful import Resource
from config.db import Session
from decorator.login_required import login_required
from model.chat import Chatroom, Chat

class ChatroomsApi(Resource):
  @login_required
  def get(self):
    s = Session()
    chatrooms_list = s.query(Chatroom).filter(Chatroom.members.any(g.uid)).all()
    for chatroom in chatrooms_list:
      chats_list = s.query(Chat).filter(Chat.chatroom_id==chatroom.get('id')).order_by(Chat.created_at).all()
      chatroom['chats'] = {
        'chats': chats_list
      }
      
    return { 'message': 'success', 'chatrooms': chatrooms_list }