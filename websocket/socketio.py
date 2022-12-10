from app import socketio
from flask_socketio import emit, join_room
from config.db import Session
from model.chat import Chat, Chatroom
from sqlalchemy.exc import SQLAlchemyError
from model.friend import Friend
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
  join_room(uid)
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

@socketio.on('friends-last-seen')
def friends_last_seen(uid):
  s = Session()
  # you invited be friend
  situation_one = s.query(Friend, User.uid, User.last_seen).join(
    User, Friend.userb_uid==User.uid
  ).filter(Friend.connected==True).filter(Friend.usera_uid==uid)
  # you received request to be friend
  situation_two = s.query(Friend, User.uid, User.last_seen).join(
    User, Friend.usera_uid==User.uid
  ).filter(Friend.connected==True).filter(Friend.userb_uid==uid)
  s.close()

  friend_connected = []

  for i in situation_one:
    situation_one_result = i._asdict()
    friend1_dict = situation_one_result.get('Friend').query_to_dict()
    friend1 = {
      'id': friend1_dict.get('id'),
      'uid': situation_one_result.get('uid'),
      'last_seen': situation_one_result.get('last_seen'),
    }
    friend_connected.append(friend1)

  for i in situation_two:
    situation_two_result = i._asdict()
    friend2_dict = situation_two_result.get('Friend').query_to_dict()
    friend2 = {
      'id': friend2_dict.get('id'),
      'uid': situation_two_result.get('uid'),
      'last_seen': situation_two_result.get('last_seen'),
    }
    friend_connected.append(friend2)
  
  emit('friends-last-seen', friend_connected)

