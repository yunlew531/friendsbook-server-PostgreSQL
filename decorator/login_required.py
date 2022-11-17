from flask_restful import request
from flask import g
import jwt
import os
from config.db import Session
from model.user import User
from time import time

def login_required(func):
  def wrapper(self, *args, **kwargs):
    # check jwt token
    authorization = request.headers.get('Authorization')
    if not authorization: return { 'message' : 'headers authorization empty' }, 401
    if not 'Bearer ' in authorization: return { 'message' : 'Authorization should be `Bearer eyJxxxxx`' }, 403
    token = authorization.split('Bearer ')[1]
    try:
      jwtDecode = jwt.decode(token, os.getenv('JWT_KEY'), algorithms=['HS256'])
      uid = jwtDecode.get('uid')
      name = jwtDecode.get('name')
    except jwt.ExpiredSignatureError: return { 'message': 'token’s exp was expired(exp)' }, 403
    except jwt.InvalidIssuedAtError: return { 'message': 'token’s issued in the future(iat)' }, 403
    except jwt.ImmatureSignatureError: return { 'message': 'token’s is not Before(nbf)' }, 403
    except jwt.InvalidKeyError: return { 'message': 'token’s is not in the proper format' }, 403
    except Exception as e: return { 'message': str(e) }, 403
    g.uid = uid
    g.name = name

    # update user last_seen
    s = Session()
    user = s.query(User).filter(User.uid==uid).first()
    if user:
      user.last_seen = time()
      s.commit()
    s.close()

    return func(self, *args, **kwargs)
  return wrapper