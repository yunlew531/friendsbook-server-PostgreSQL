from flask import Flask
from flask_restful import Api
from dotenv import load_dotenv
load_dotenv()
from flask_cors import CORS
from api.image import ImageApi, ImagesApi, BannerImgApi, AvatarImgApi
from api.account import AccountApi, LoginLogoutApi
from api.user import UserAuthApi, UserApi
from api.article import ArticleApi, ArticlesByUidApi, ArticleLikeApi, CommentApi, CommentsApi
from api.friend import FriendsConnectedByUidApi, RecommendFriendApi, FriendInviteApi, FriendsApi, FriendShipApi

app = Flask(__name__)
api = Api(app)

# cors
cors = CORS(app, resources={r'/api/*': {'origins': ['http://localhost:3000']}})

# api
# user api
api.add_resource(UserAuthApi, '/api/user', methods=['GET'], endpoint='personal_user_profile')
api.add_resource(UserApi, '/api/user/<user_uid>', methods=['GET'], endpoint='user_by_uid')
api.add_resource(AccountApi, '/api/account', methods=['POST'], endpoint='account')
api.add_resource(LoginLogoutApi, '/api/account/login', methods=['POST'], endpoint='login')
api.add_resource(LoginLogoutApi, '/api/account/logout', methods=['GET'], endpoint='logout')

# article api
api.add_resource(ArticleApi, '/api/article', methods=['POST'], endpoint='article')
api.add_resource(ArticleApi, '/api/article/<article_id>', methods=['DELETE'], endpoint='article_article_id')
api.add_resource(ArticleApi, '/api/articles', methods=['GET'], endpoint='articles')
api.add_resource(ArticleLikeApi, '/api/article/<article_id>/thumbsup', methods=['GET', 'POST'], endpoint='article_like')
api.add_resource(CommentApi, '/api/article/<article_id>/comment', methods=['POST'], endpoint='comment')
api.add_resource(CommentsApi, '/api/article/<article_id>/comments', methods=['GET'], endpoint='comments')
api.add_resource(ArticlesByUidApi, '/api/articles/<user_uid>', methods=['GET'], endpoint='articles_by_uid')

# friend api
api.add_resource(RecommendFriendApi, '/api/friends/recommend/<num>', methods=['GET'], endpoint='friends_recommend')
api.add_resource(FriendInviteApi, '/api/friend/invite/<user_uid>', methods=['POST'], endpoint='invite_friend')
api.add_resource(FriendInviteApi, '/api/friend/invite/<friend_id>', methods=['PATCH', 'DELETE'], endpoint='friend')
api.add_resource(FriendShipApi, '/api/friend/<friend_id>', methods=['DELETE'], endpoint='delete_friend')
api.add_resource(FriendsApi, '/api/friends', methods=['GET'], endpoint='friends')
api.add_resource(FriendsConnectedByUidApi, '/api/friends/<user_uid>', methods=['GET'], endpoint='friends_connected')

# image api
api.add_resource(ImageApi, '/api/image', methods=['POST'], endpoint='image')
api.add_resource(ImageApi, '/api/image/<image_id>', methods=['DELETE'], endpoint='image_id')
api.add_resource(BannerImgApi, '/api/image/banner', methods=['POST'], endpoint='banner_image')
api.add_resource(AvatarImgApi, '/api/image/avatar', methods=['POST'], endpoint='avatar_image')
api.add_resource(ImagesApi, '/api/images/<user_uid>', methods=['GET'], endpoint='images')

if __name__ == '__main__':
  app.run()