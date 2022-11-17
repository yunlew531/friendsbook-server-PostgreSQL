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
    users_query = s.query(User.uid, User.name, User.nickname, User.last_seen)
    s.close()
    count = users_query.count()
    user_model_list = users_query.all()

    if pick_num > count: pick_num = count

    # TODO: exclude friends you have, add last_seen
    user_list = []
    random_list = []
    while len(random_list) < pick_num:
      num = randint(0, count - 1)
      if num not in random_list:
        random_list.append(num)
    
    for i in random_list:
      user_model = user_model_list[i]
      user_list.append({
        'uid': user_model.uid,
        'name': user_model.name,
        'nickname': user_model.nickname,
        'last_seen': user_model.last_seen
      })

    return { 'message': 'success', 'users': user_list }

class FriendApi(Resource):
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

