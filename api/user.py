from flask_restful import Resource
from config.db import s
from model.user import User as UserModel

class UserApi(Resource):
  def get(self):
    user = UserModel()
    user.name = 'mike'
    user.age = 120
    user.email = 'mike@example.com'
    user.password = '55555'
    s.add(user)
    s.commit()


    # user = s.query(UserModel).first()
    return {'name': 'user.get_name()'}