from flask_restful import Resource
from config.db import Session
from model.article import Article
from model.user import User
from decorator.login_required import login_required
from flask import g

class UserApi(Resource):
  # get user profile by uid
  def get(self, user_uid):
    s = Session()
    user_row = s.query(
      User.uid, User.name, User.age, User.email, User.created_at, User.nickname
    ).filter(User.uid==user_uid).first()
    s.close()
    if not user_row: return { 'message': 'user not found' }, 404
    user_dict = user_row._asdict()
    
    return {'message': 'success', 'profile': user_dict }

class UserAuthApi(Resource):
  # use jwt token get personal user profile
  @login_required
  def get(self):
    s = Session()
    user_row = s.query(
      User.uid, User.name, User.age, User.email, User.created_at, User.nickname
    ).filter(User.uid==g.uid).first()
    s.close()
    if not user_row: return { 'message': 'user not found' }, 404
    user_dict = user_row._asdict()
    
    return {'message': 'success', 'profile': user_dict }