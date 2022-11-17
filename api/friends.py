from flask_restful import Resource
from config.db import Session
from decorator.login_required import login_required
from model.user import User
from random import randint

class RecommendFriend(Resource):
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