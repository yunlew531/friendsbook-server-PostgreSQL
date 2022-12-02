try:
  from __main__ import socketio
except ImportError:
  from socketservice import socketio
from flask_socketio import emit, join_room
from config.db import Session
from model.chat import Chat, Chatroom
from sqlalchemy.exc import SQLAlchemyError

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
  emit('join-chatrooms-success', 'join success')

# join chatroom by chatroom id
@socketio.on('join-chatroom')
def join_chatroom(chatroom_id):
  join_chatroom(chatroom_id)

# send message in specify chatroom
@socketio.on('chat')
def chat(data):
  chat = Chat()
  chat.content = data.get('content')
  chat.chatroom_id = data.get('chatroom_id')
  chat.user_uid = data.get('user_uid')
  s = Session()
  s.add(chat)

  try: 
    s.commit()
    s.refresh(chat)
  except SQLAlchemyError as e: print(e)
  finally: s.close()

  emit('message', chat.query_to_dict(), to=data.get('chatroom_id'))