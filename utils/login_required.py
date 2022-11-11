from flask_restful import request
from flask import g
import jwt
import os

def login_required(func):
  def wrapper(self):
    authorization = request.headers.get('Authorization')
    if not authorization: return { 'message' : 'headers authorization empty' }, 401
    if not 'Bearer ' in authorization: return { 'message' : 'Authorization invalid' }, 403
    token = authorization.split('Bearer ')[1]
    try:
      jwtDecode = jwt.decode(token, os.getenv('JWT_KEY'), algorithms=['HS256'])
      uid = jwtDecode.get('uid')
      name = jwtDecode.get('name')
    except Exception as e:
      return { 'message': e }, 403
    g.uid = uid
    g.name = name
    return func(self)
  return wrapper