from flask import g
from flask_restful import Resource, request
from config.db import Session
from decorator.login_required import login_required
from sqlalchemy.exc import SQLAlchemyError
from model.chat import Chatroom, Chat
from model.user import User

class ChatroomsApi(Resource):
  # get chatrooms with chats
  @login_required
  def get(self):
    s = Session()
    chatrooms_query = s.query(Chatroom).filter(Chatroom.members.any(g.uid))
    chatrooms_list = []
    for chatroom in chatrooms_query:
      chatroom = chatroom.query_to_dict()
      chats_list = []
      chatrooms_rows = s.query(Chat, User.uid, User.name, User.nickname, User.avatar_url).join(
        User, Chat.user_uid==User.uid
      ).filter(Chat.chatroom_id==chatroom.get('id')).order_by(Chat.created_at)
      for chatrooms_row in chatrooms_rows:
        chat_result = chatrooms_row._asdict()
        chats_list.append({
          **chat_result.get('Chat').query_to_dict(),
          'author': {
            'name': chat_result.get('name'),
            'nickname': chat_result.get('nickname'),
            'uid': chat_result.get('uid'),
            'avatar_url': chat_result.get('avatar_url'),
          }
        })
      chatroom['chats'] = chats_list

      # type one to one get chatroom name (user name)
      type = chatroom.get('type')
      if type == 1:
        members = chatroom.get('members')
        for m in members:
          if not m == g.uid:
            other_side_user = m

        user_row = s.query(User.name, User.nickname, User.avatar_url).filter(User.uid==other_side_user).first()
        user_dict = user_row._asdict()
        nickname = user_dict.get('nickname')
        name = user_dict.get('name')
        avatar_url = user_dict.get('avatar_url')
        chatroom['name'] = nickname or name        
        chatroom['avatar_url'] = avatar_url    

      chatrooms_list.append(chatroom)
      
    return { 'message': 'success', 'chatrooms': chatrooms_list }


class ChatroomApi(Resource):
  # create multiple people chatroom
  @login_required
  def post(self):
    body = request.get_json()
    members = body.get('members')
    name = body.get('name')
    avatar_url = body.get('avatar_url')

    chatroom = Chatroom()
    chatroom.members = members
    chatroom.type = 2
    
    if len(name) > 10: return { 'message': 'name too long' }, 400

    chatroom.name = name
    chatroom.avatar_url = avatar_url

    s = Session()
    s.add(chatroom)

    try:
      from app import socketio
      s.commit()
      s.refresh(chatroom)

      for m in members:
        if m != g.uid:
          socketio.emit('get-chatroom', chatroom.query_to_dict(), to=m)
        else:
          socketio.emit('join-chatroom', chatroom.query_to_dict().get('id'), to=g.uid)

    except SQLAlchemyError as e:
      print(e)
      return {'message': 'something wrong' }, 500
    finally: s.close()

    return { 'message': 'success', 'chatroom': chatroom.query_to_dict() }