from flask import g
from flask_restful import Resource
from config.db import Session
from decorator.login_required import login_required
from model.friend import Friend
from model.user import User
from random import randint
from sqlalchemy.exc import SQLAlchemyError

class RecommendFriendApi(Resource):
  # return recommend friends
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
    if pick_num > count - len(friend_list): pick_num = count - len(friend_list) - 1

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

class FriendApi(Resource):
  # add friend by uid
  @login_required
  def get(self, user_uid):
    s = Session()
    user = s.query(User).filter(User.uid==user_uid).first()
    if not user: return { 'message': 'user not found' }, 404

    situation_one = s.query(Friend).filter(Friend.usera_uid==g.uid).filter(Friend.userb_uid==user_uid).first()
    situation_two = s.query(Friend).filter(Friend.userb_uid==g.uid).filter(Friend.usera_uid==user_uid).first()
    is_friend = situation_one or situation_two
    if is_friend: return { 'message': 'you are already friends' }, 403

    friend = Friend(
      usera_uid=g.uid,
      userb_uid=user_uid,
    )
    s.add(friend)
    try: s.commit()
    except SQLAlchemyError: return { 'message': 'something wrong' }, 500
    finally: s.close()

    return { 'message':'success' }

  # delete friend by uid
  @login_required
  def delete(self, user_uid):
    s = Session()
    user = s.query(User).filter(User.uid==user_uid).first()
    if not user: return { 'message': 'user not found' }, 404

    situation_one = s.query(Friend).filter(Friend.usera_uid==g.uid).filter(Friend.userb_uid==user_uid).first()
    situation_two = s.query(Friend).filter(Friend.userb_uid==g.uid).filter(Friend.usera_uid==user_uid).first()
    is_friend = situation_one or situation_two
    if not is_friend: return { 'message': "you're not friends" }, 403

    friend = situation_one or situation_two

    s.delete(friend)
    try: s.commit()
    except SQLAlchemyError: return {'message':'something wrong' }, 500
    finally: s.close()

    return { 'message': 'success' }

class FriendsApi(Resource):
  # get friends list by jwt token
  @login_required
  def get(self):
    s = Session()
    situation_one = s.query(Friend, User.uid, User.name, User.nickname, User.last_seen).join(
      User, Friend.usera_uid==User.uid
    ).filter(Friend.userb_uid==g.uid)
    situation_two = s.query(Friend, User.uid, User.name, User.nickname, User.last_seen).join(
      User, Friend.userb_uid==User.uid
    ).filter(Friend.usera_uid==g.uid)
    s.close()

    friend_list = []
    for i in situation_one:
      situation_one_result = i._asdict()
      friend1_dict = situation_one_result.get('Friend').query_to_dict()
      friend_list.append({
        'became_friend_time': friend1_dict.get('became_friend_time'),
        'uid': situation_one_result.get('uid'),
        'name': situation_one_result.get('name'),
        'nickname': situation_one_result.get('nickname'),
        'last_seen': situation_one_result.get('last_seen'),
      })
    for i in situation_two:
      situation_two_result = i._asdict()
      friend2_dict = situation_two_result.get('Friend').query_to_dict()
      friend_list.append({
        'became_friend_time': friend2_dict.get('became_friend_time'),
        'uid': situation_two_result.get('uid'),
        'name': situation_two_result.get('name'),
        'nickname': situation_two_result.get('nickname'),
        'last_seen': situation_two_result.get('last_seen'),
      })

    return { 'message':'success', 'friends': friend_list }

