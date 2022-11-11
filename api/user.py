from flask_restful import Resource
from config.db import s
from model.user import User as UserModel

class User(Resource):
  def get(self):
    # user1 = UserModel()
    # user1.name = 'mike'
    # user1.age = 120
    # s.add(user1)
    # s.commit()

    user = s.query(UserModel).first()
    return {'name': user.get_name()}