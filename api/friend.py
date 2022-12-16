from flask import g
from flask_restful import Resource
from config.db import Session
from decorator.login_required import login_required
from model.chat import Chat, Chatroom
from model.friend import Friend
from model.notification import Notification
from model.user import User
from random import randint
from sqlalchemy.exc import SQLAlchemyError
from time import time

class RecommendFriendApi(Resource):
  # return recommend friends list
  @login_required
  def get(self, num):
    pick_num = int(num)
    s = Session()

    # get friends you have
    situation_one = s.query(Friend.usera_uid, User.uid).join(
      User, Friend.usera_uid==User.uid
    ).filter(Friend.userb_uid==g.uid)
    situation_two = s.query(Friend.userb_uid, User.uid).join(
      User, Friend.userb_uid==User.uid
    ).filter(Friend.usera_uid==g.uid)

    friend_list = []
    for i in situation_one:
      friend_list.append(i._asdict().get('uid'))
    for i in situation_two:
      friend_list.append(i._asdict().get('uid'))

    # get users to random
    users_query = s.query(User.uid, User.name, User.nickname, User.last_seen)
    s.close()
    count = users_query.count()
    user_model_list = users_query.all()

    if pick_num > count: pick_num = count
    if pick_num >= count - len(friend_list): pick_num = count - len(friend_list) - 1

    # random user list
    user_list = []
    while True:
      idx = randint(0, count - 1)
      user_model = user_model_list[idx]

      # exclude friends you have
      if not user_model.uid in friend_list and not user_model.uid==g.uid:
        user = {
          'uid': user_model.uid,
          'name': user_model.name,
          'nickname': user_model.nickname,
          'last_seen': user_model.last_seen
        }
        if not user in user_list:
          user_list.append(user)
      if len(user_list) >= pick_num: break
    
    return { 'message': 'success', 'users': user_list }

class FriendInviteApi(Resource):
  # create friend invite by uid
  @login_required
  def post(self, user_uid):
    s = Session()
    user = s.query(User).filter(User.uid==user_uid).first()
    if not user: return { 'message': 'user not found' }, 404

    # you invited be friend
    situation_one = s.query(Friend).filter(Friend.usera_uid==g.uid).filter(Friend.userb_uid==user_uid).first()
    # you received request to be friend
    situation_two = s.query(Friend).filter(Friend.userb_uid==g.uid).filter(Friend.usera_uid==user_uid).first()
    is_friend = situation_one or situation_two
    if is_friend:
      if is_friend.connected: return { 'message': 'you are already friends' }, 403
      else: return { 'message': 'you sent the request before' }, 403

    friend = Friend(
      usera_uid=g.uid,
      userb_uid=user_uid,
    )

    notification = Notification(
      user_uid=user_uid,
      invited_from=g.uid,
      type=1,  # friend invited
    )

    s.add(friend)
    s.add(notification)
    try: s.commit()
    except SQLAlchemyError as e: 
      print(e)
      return { 'message': 'something wrong' }, 500
    finally: s.close()

    return { 'message':'success' }

  # agree friend connected
  @login_required
  def patch(self, friend_id):
    s = Session()
    friend = s.query(Friend).filter(Friend.id==friend_id).first()
    if not friend: return { 'message': 'friend_id not found' }, 404
    if friend.userb_uid!= g.uid: return { 'message': "you're not invited in this friend_id" }, 403

    friend.connected_time = time()
    friend.connected = True

    chatroom = Chatroom()
    chatroom.members = [friend.usera_uid, friend.userb_uid]
    chatroom.type = 1

    for m in chatroom.members:
      if m != g.uid: user_uid = m
    other_user_row = s.query(User.name).filter(User.uid==user_uid).first()
    other_user_dict = other_user_row._asdict()

    self_user_row = s.query(User.name).filter(User.uid==g.uid).first()
    self_user_dict = self_user_row._asdict()

    s.add(chatroom)

    try:
      from app import socketio
      s.commit()
      s.refresh(chatroom)
      chatroom_dict = {**chatroom.query_to_dict()}
      socketio.emit('get-chatroom', {**chatroom_dict, 'name': other_user_dict.get('name')}, to=g.uid)
      socketio.emit('get-chatroom', {**chatroom_dict, 'name': self_user_dict.get('name')}, to=user_uid)
    except SQLAlchemyError: return {'message':'something wrong' }, 500
    finally: s.close()
    return { 'message': 'success' }

  # remove friend invite by friend_id
  # refuse invite or cancel invite
  @login_required
  def delete(self, friend_id):
    s = Session()
    friend = s.query(Friend).filter(Friend.id==friend_id).first()
    if not friend: return { 'message': "friend_id not found" }, 404

    try:
      if friend.usera_uid==g.uid or friend.userb_uid==g.uid:
        s.delete(friend)
        s.commit()
      else:
        return { 'message': "you are not in this friend_id" }, 403
    except SQLAlchemyError: return {'message':'something wrong' }, 500
    finally: s.close()

    if friend.usera_uid==g.uid: code = 1  # cancel invite
    else: code = 2  # refuse invite

    return { 'message': 'success', 'code': code }

class FriendShipApi(Resource):
  # delete friend
  @login_required
  def delete(self, friend_id):
    s = Session()
    friend = s.query(Friend).filter(Friend.id==friend_id).first()
    if not friend: return { 'message': "friend_id not found" }, 404

    if friend.usera_uid==g.uid or friend.userb_uid==g.uid:
      members = [friend.usera_uid, friend.userb_uid]
      chatroom = s.query(Chatroom).filter(Chatroom.members.contains(members)).first()
      chats_query = s.query(Chat).filter(Chat.chatroom_id==chatroom.id)

      for chat_query in chats_query:
        s.delete(chat_query)

      s.delete(friend)
      s.delete(chatroom)
    else:
      return { 'message': "you are not in this friend_id" }, 403
    
    try: s.commit()
    except SQLAlchemyError: return {'message':'something wrong' }, 500
    finally: s.close()

    return { 'message': 'success' }

class FriendsApi(Resource):
  # get connected, received, sent friends dict by jwt token
  @login_required
  def get(self):
    s = Session()

    # you invited be friend
    situation_one = s.query(Friend, User.uid, User.name, User.nickname, User.last_seen, User.avatar_url).join(
      User, Friend.userb_uid==User.uid
    ).filter(Friend.usera_uid==g.uid)
    # you received request to be friend
    situation_two = s.query(Friend, User.uid, User.name, User.nickname, User.last_seen, User.avatar_url).join(
      User, Friend.usera_uid==User.uid
    ).filter(Friend.userb_uid==g.uid)
    s.close()

    friend_data = {
      'connected': [],
      'received': [],
      'sent': [],
    }

    for i in situation_one:
      situation_one_result = i._asdict()
      friend1_dict = situation_one_result.get('Friend').query_to_dict()
      friend1 = {
          'id': friend1_dict.get('id'),
          'connected_time': friend1_dict.get('connected_time'),
          'invited_time': friend1_dict.get('invited_time'),
          'connected': friend1_dict.get('connected'),
          'uid': situation_one_result.get('uid'),
          'name': situation_one_result.get('name'),
          'nickname': situation_one_result.get('nickname'),
          'last_seen': situation_one_result.get('last_seen'),
          'avatar_url': situation_one_result.get('avatar_url'),
        }
      if friend1_dict['connected']:
        friend_data['connected'].append(friend1)
      else:
        friend_data['sent'].append(friend1)

    for i in situation_two:
      situation_two_result = i._asdict()
      friend2_dict = situation_two_result.get('Friend').query_to_dict()
      friend2 = {
        'id': friend2_dict.get('id'),
        'connected_time': friend2_dict.get('connected_time'),
        'invited_time': friend2_dict.get('invited_time'),
        'connected': friend2_dict.get('connected'),
        'uid': situation_two_result.get('uid'),
        'name': situation_two_result.get('name'),
        'nickname': situation_two_result.get('nickname'),
        'last_seen': situation_two_result.get('last_seen'),
        'avatar_url': situation_two_result.get('avatar_url'),
      }
      if friend2_dict['connected']:
        friend_data['connected'].append(friend2)
      else:
        friend_data['received'].append(friend2)
   
    return { 'message':'success', 'friends': friend_data }

class FriendsConnectedByUidApi(Resource):
  # get connected friends list by uid
  def get(self, user_uid):
    s = Session()
    user = s.query(User).filter(User.uid==user_uid).first()
    if not user: return { 'message': 'user not found' }, 404
    connected_friends = []

    # you invited be friend
    situation_one = s.query(Friend, User.uid, User.name, User.nickname, User.avatar_url).join(
      User, Friend.userb_uid==User.uid
    ).filter(Friend.usera_uid==user_uid).filter(Friend.connected==True)
    for friend in situation_one:
      friend1_dict = friend._asdict()
      connected_friends.append({
        **friend1_dict.get('Friend').query_to_dict(),
        'uid': friend1_dict.get('uid'),
        'name': friend1_dict.get('name'),
        'nickname': friend1_dict.get('nickname'),
        'avatar_url': friend1_dict.get('avatar_url'),
      })
   
    # you received request to be friend
    situation_two = s.query(Friend, User.uid, User.name, User.nickname, User.avatar_url).join(
      User, Friend.usera_uid==User.uid
    ).filter(Friend.userb_uid==user_uid).filter(Friend.connected==True)
    for friend in situation_two:
      friend2_dict = friend._asdict()
      connected_friends.append({
        **friend2_dict.get('Friend').query_to_dict(),
        'uid': friend2_dict.get('uid'),
        'name': friend2_dict.get('name'),
        'nickname': friend2_dict.get('nickname'),
        'avatar_url': friend2_dict.get('avatar_url'),
      })

    s.close()
    return { 'message': 'success', 'friends': connected_friends }