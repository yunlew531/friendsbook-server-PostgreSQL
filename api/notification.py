from flask_restful import Resource


class NotificationsApi(Resource):
  def get(self):
    return { 'message': 'success', 'notifications': ''}
