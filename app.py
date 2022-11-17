from flask import Flask
from flask_restful import Api
from dotenv import load_dotenv
load_dotenv()
from flask_cors import CORS
from api.account import AccountApi, LoginLogoutApi
from api.user import UserAuthApi
from api.article import ArticleApi, ArticleThumbsUpApi, CommentApi, CommentsApi ,Test
from api.friend import RecommendFriendApi, FriendApi, FriendsApi

app = Flask(__name__)
api = Api(app)

# cors
cors = CORS(app, resources={r'/api/*': {'origins': ['http://localhost:3000']}})

# api
api.add_resource(UserAuthApi, '/api/user', methods=['GET'], endpoint='personal_user_profile')
api.add_resource(AccountApi, '/api/account', methods=['POST'], endpoint='account')
api.add_resource(LoginLogoutApi, '/api/account/login', methods=['POST'], endpoint='login')
api.add_resource(LoginLogoutApi, '/api/account/logout', methods=['GET'], endpoint='logout')
api.add_resource(ArticleApi, '/api/article', methods=['POST'], endpoint='article')
api.add_resource(ArticleApi, '/api/articles', methods=['GET'], endpoint='articles')
api.add_resource(Test, '/api/test', methods=['GET'], endpoint='test')
api.add_resource(CommentApi, '/api/article/<article_id>/comment', methods=['POST'], endpoint='comment')
api.add_resource(CommentsApi, '/api/article/<article_id>/comments', methods=['GET'], endpoint='comments')
api.add_resource(ArticleThumbsUpApi, '/api/article/<article_id>/thumbsup', methods=['GET', 'POST'], endpoint='article_thumbsup')
api.add_resource(RecommendFriendApi, '/api/friends/recommend/<num>', methods=['GET'], endpoint='friends_recommend')
api.add_resource(FriendApi, '/api/friend/add/<user_uid>', methods=['GET', 'DELETE'], endpoint='friend')
api.add_resource(FriendsApi, '/api/friends', methods=['GET'], endpoint='friends')

if __name__ == '__main__':
  app.run()