from flask import Flask
from flask_restful import Api
from dotenv import load_dotenv
load_dotenv()
from flask_cors import CORS
from api.account import AccountApi, LoginLogoutApi
from api.user import UserAuthApi
from api.article import ArticleApi, CommentApi ,Test

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

if __name__ == '__main__':
  app.run()