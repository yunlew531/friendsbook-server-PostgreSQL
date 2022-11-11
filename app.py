from flask import Flask
from flask_restful import Api
from dotenv import load_dotenv
load_dotenv()
from flask_cors import CORS
from api.account import AccountApi, LoginLogoutApi
from api.user import UserAuthApi

app = Flask(__name__)
api = Api(app)

# cors
cors = CORS(app, resources={r'/api/*': {'origins': ['http://localhost:3000']}})

# api
api.add_resource(UserAuthApi, '/api/user', methods=['GET'], endpoint='personal_user_profile')
api.add_resource(AccountApi, '/api/account', methods=['POST'], endpoint='account')
api.add_resource(LoginLogoutApi, '/api/account/login', methods=['POST'], endpoint='login')
api.add_resource(LoginLogoutApi, '/api/account/logout', methods=['GET'], endpoint='logout')

if __name__ == '__main__':
  app.run()