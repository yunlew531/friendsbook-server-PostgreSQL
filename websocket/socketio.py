from app import socketio
from flask_socketio import emit, join_room
from config.db import Session
from model.chat import Chat, Chatroom
from sqlalchemy.exc import SQLAlchemyError
from model.user import User

# broadcast to all connected clients
@socketio.on('broadcast')
def broadcast(message):
  emit('broadcast', message, broadcast=True)

# when enter website, connect all chatrooms you join
@socketio.on('join-chatrooms')
def join_chatrooms(uid):
  s = Session()
  chatrooms = s.query(Chatroom).filter(Chatroom.members.any(uid)).all()
  s.close()
  for chatroom in chatrooms:
    join_room(chatroom.id)
  emit('message', 'join chatroom success')

# join chatroom by chatroom id
@socketio.on('join-chatroom')
def join_chatroom(chatroom_id):
  join_room(chatroom_id)

# send message in specify chatroom
@socketio.on('chat')
def chat(data):
  user_uid = data.get('user_uid')
  chat = Chat()
  chat.content = data.get('content')
  chat.chatroom_id = data.get('chatroom_id')
  chat.user_uid = user_uid
  s = Session()
  s.add(chat)

  user = s.query(User.uid, User.name, User.nickname, User.avatar_url).filter(User.uid==user_uid).first()
  if not user: 
    emit('error-message', 'User not found')
    s.close()
    return;
  
  author = {
    'uid': user.uid,
    'name': user.name,
    'nickname': user.nickname,
    'avatar_url': user.avatar_url
  }

  try: 
    s.commit()
    s.refresh(chat)
    chat_dict = chat.query_to_dict()
    chat_dict['author'] = author
  except SQLAlchemyError as e: print(e)
  finally: s.close()

  emit('chat', chat_dict, to=data.get('chatroom_id'))