from flask import Flask
from flask_restful import Api
from dotenv import load_dotenv
load_dotenv()
from api.user import User

app = Flask(__name__)
api = Api(app)

api.add_resource(User, '/')

if __name__ == '__main__':
  app.run()