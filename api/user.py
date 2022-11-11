from flask_restful import Resource
from config.db import BASE, s
from model.user import User
from utils.login_required import login_required
from flask import g

# class UserApi(Resource):
#   def get(self):
#     user = User()
#     user.name = 'mike'
#     user.age = 120
#     user.email = 'mike@example.com'
#     user.password = '55555'
#     s.add(user)
#     s.commit()

#     # user = s.query(UserModel).first()
#     return {'name': 'user.get_name()'}

class UserAuthApi(Resource):
  @login_required
  def get(self):
    # use jwt token get personal user profile
    user_row = s.query(
      User.uid, User.name, User.age, User.email, User.created_at, User.nickname
    ).filter(User.uid==g.uid).first()
    if not user_row: return { 'message': 'user not found' }, 404
    select_list = ['uid', 'name', 'age', 'email', 'created_at', 'nickname']
    user_dict = BASE().row_to_dict(user_row, select_list)
    
    return {'message': 'success', 'profile': user_dict }