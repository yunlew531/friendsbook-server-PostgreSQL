from flask_restful import request
from flask import g
import jwt
import os

def login_required(func):
  def wrapper(self):
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
    return func(self)
  return wrapper