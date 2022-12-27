from flask_restful import Resource, request
from config.db import Session
from model.article import Article
from model.user import User
from decorator.login_required import login_required
from sqlalchemy.exc import SQLAlchemyError
from flask import g

class UserApi(Resource):
  # get user profile by uid
  def get(self, user_uid):
    print(5)
    s = Session()
    user_row = s.query(
      User.uid, User.name, User.age, User.email, User.created_at, User.nickname, User.banner_url, User.avatar_url, User.city, User.alternate_email
    ).filter(User.uid==user_uid).first()
    s.close()
    if not user_row: return { 'message': 'user not found' }, 404
    user_dict = user_row._asdict()
    
    return { 'message': 'success', 'profile': user_dict }

class UserAuthApi(Resource):
  # use jwt token get personal user profile
  @login_required
  def get(self):
    s = Session()
    user_row = s.query(
      User.uid, User.name, User.age, User.email, User.created_at, User.nickname, User.banner_url, User.avatar_url, User.city, User.alternate_email
    ).filter(User.uid==g.uid).first()
    s.close()
    if not user_row: return { 'message': 'user not found' }, 404
    user_dict = user_row._asdict()
    
    return { 'message': 'success', 'profile': user_dict }

  @login_required
  def patch(self, profile_key):
    value = request.get_json().get('value')
    s = Session()
    user = s.query(User).filter(User.uid==g.uid).first()

    if profile_key=='name':
      user.name = value

    if profile_key=='city':
      user.city = value

    try: 
      s.commit()
      s.refresh(user)
    except SQLAlchemyError: return { 'message': 'something error' }, 500
    finally: s.close()

    return { 'message': 'success', profile_key: getattr(user, profile_key) }

# alternate_email
class UserEmail(Resource):
  @login_required
  def post(self, email):
    s = Session()
    user = s.query(User).filter(User.uid==g.uid).first()

    emails = user.alternate_email or []
    if email in emails:
      return { 'message': 'email already exists' }, 400
    else:
      emails.append(email)
    print(emails)
    print(user.alternate_email)
    
    user.alternate_email = emails

    try:
      s.commit()
      s.refresh(user)
    except SQLAlchemyError as e: 
      print(e)
      return { 'message':'something error' }, 500
    finally: s.close()

    return { 'message': 'success', 'alternate_email': user.alternate_email }
