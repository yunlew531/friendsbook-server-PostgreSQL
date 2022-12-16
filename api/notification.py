from flask import g
from flask_restful import Resource
from config.db import Session
from decorator.login_required import login_required
from model.notification import Notification
from model.user import User

class NotificationsApi(Resource):
  @login_required
  def get(self):
    s = Session()
    notifications_rows = s.query(Notification, User.uid, User.name, User.nickname).join(
      User, User.uid==Notification.invited_from 
    ).filter(Notification.user_uid==g.uid)
    s.close()

    notifications_dict = []
    for n_row in notifications_rows:
      n_result = n_row._asdict()
      notifications_dict.append({
        **n_result.get('Notification').query_to_dict(),
        'invited_from': {
          'uid': n_result.get('uid'),
          'name': n_result.get('name'),
          'nickname': n_result.get('nickname'),
        }
      })

    return { 'message': 'success', 'notifications': notifications_dict }
