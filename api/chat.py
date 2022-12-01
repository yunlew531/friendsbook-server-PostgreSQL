from flask import g
from flask_restful import Resource, request
from config.db import Session
from decorator.login_required import login_required
from sqlalchemy.exc import SQLAlchemyError
from model.chat import Chatroom, Chat

class ChatroomsApi(Resource):
  @login_required
  def get(self):
    s = Session()
    chatrooms_query = s.query(Chatroom).filter(Chatroom.members.any(g.uid))
    chatrooms_list = []
    for chatroom in chatrooms_query:
      chatroom = chatroom.query_to_dict()
      chats_list = []
      chatrooms_query = s.query(Chat).filter(Chat.chatroom_id==chatroom.get('id')).order_by(Chat.created_at)
      for chat in chatrooms_query:
        chat = chat.query_to_dict()
        chats_list.append(chat)
      chatroom['chats'] = chats_list
      chatrooms_list.append(chatroom)
      
    return { 'message': 'success', 'chatrooms': chatrooms_list }


class ChatroomApi(Resource):
  # create one to one chatroom or multiple people chatroom
  @login_required
  def post(self):
    body = request.get_json()
    members = body.get('members')
    type = body.get('type')
    name = body.get('name')
    avatar_url = body.get('avatar_url')

    s = Session()
    
    # one to one chatroom
    if type == 1:
      if not len(members) == 2: return { 'message', 'one to one chatroom required two members' }, 400
      chatroom = s.query(Chatroom).filter(Chatroom.members.contains(members)).first()
      if chatroom: return { 'message': 'chatroom exist' }, 400
      
      chatroom = Chatroom()
      chatroom.members = members
      chatroom.type = type
      chatroom.avatar_url = avatar_url
      s.add(chatroom)
    
    # multiple people chatroom
    if type == 2:
      chatroom.name = name
      # TODO:
    
    try:
      s.commit()
      s.refresh(chatroom)
    except SQLAlchemyError as e:
      print(e)
      return {'message': 'something wrong' }, 500
    finally: s.close()

    return { 'message': 'success', 'chatroom': chatroom.query_to_dict() }