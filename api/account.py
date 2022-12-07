from flask_restful import Resource, request
from decorator.login_required import login_required
from model.user import User
from flask_bcrypt import Bcrypt
from config.db import Session
import re
import jwt
import os
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError

bcrypt = Bcrypt()
regex_email = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

class AccountApi(Resource):
  # create account
  def post(self):
    body = request.get_json()
    email = body.get('email')
    name = body.get('name')
    password = body.get('password')

    if not name: return { 'message': 'name required.', 'code': 2 }, 400
    if not email: return { 'message': 'email required.', 'code': 3 }, 400
    if not password: return { 'message': 'password required.', 'code': 4 }, 400

    s = Session()
    user_query = s.query(User).filter(User.email==email).first()
    if user_query: return { 'message': 'email is exists.', 'code': 1 }, 303
    if type(password) != str: return { 'message': 'password should be string', 'code': 5 }, 400
    if not re.fullmatch(regex_email, email): return { 'message': 'email invalid', 'code': 6 }, 400
    if type(name) != str: return { 'message': 'name should be string', 'code': 7 }, 400
    if len(name) < 2: return { 'message': 'name too short', 'code': 8 }, 400
    if len(password) < 6: return { 'message': 'password too short', 'code': 9 }, 400
    hash_password = bcrypt.generate_password_hash(password=password).decode('utf-8')

    user = User(
      email = email,
      password = hash_password,
      name = name
    )
    s.add(user)
    try: s.commit()
    except SQLAlchemyError: return { 'message': 'something wrong' }, 500
    finally: s.close()

    return { 'message': 'create success' }, 201

class LoginLogoutApi(Resource):
  # logout
  def get(self):
    return { 'message': 'success' }
  # login
  def post(self):
    body = request.get_json()
    email = body.get('email')
    password = body.get('password')
    account_type = request.args.get('account_type')
    print(account_type)
    if account_type == 'test':
      email = os.getenv('TEST_ACCOUNT_EMAIL')
      password = os.getenv('TEST_ACCOUNT_PASSWORD')
    print(email, password)

    if not email: return { 'message': 'email required.', 'code': 1 }, 400
    if not password: return { 'message': 'password required.', 'code': 2 }, 400
    if len(password) < 6: return { 'message': 'password must be at least 6 characters.', 'code': 3 }, 400
    
    s = Session()
    user_query = s.query(User).filter(User.email==email).first()
    s.close()
    if not user_query: return { 'message': 'user not found.', 'code': 4 }, 404

    user_dict = user_query.query_to_dict()
    hash_password = user_dict.get('password')
    is_password_valid = bcrypt.check_password_hash(hash_password, password)
    if not is_password_valid: return { 'message': 'password is wrong.', 'code': 5}, 400
    uid = user_dict.get('uid')
    name = user_dict.get('name')
    jwt_exp = datetime.now() + timedelta(days=7)
    jwt_token = jwt.encode({'uid': uid, 'name': name, 'exp': jwt_exp}, os.getenv('JWT_KEY'), algorithm="HS256")
    return { 'message': 'success', 'token': jwt_token, 'uid': uid }
