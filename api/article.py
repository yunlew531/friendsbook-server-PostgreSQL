from flask import g
from flask_restful import Resource, request
from config.db import Session
from sqlalchemy.exc import SQLAlchemyError
from decorator.login_required import login_required
from model.article import Article
from model.user import User

class ArticleApi(Resource):
  @login_required
  # get personal page article
  def get(self):
    s = Session()
    articles_rows = s.query(Article, User.name).join(
      User, Article.user_uid==User.uid
    ).filter(Article.user_uid==g.uid)
    s.close()
    articles_list = []
    for article in articles_rows:
      article = article._asdict()
      articles_list.append({
        **article.get('Article').query_to_dict(),
        'author': {
          'name': article.get('name'),
          'uid': g.uid
        }
      })
    return { 'message': 'success', 'articles': articles_list }
  @login_required
  def post(self):
    # post article on personal page
    body = request.get_json()
    content = body.get('content')
    if not content: return { 'message': 'content required', 'code': 1 }, 400

    article = Article(content=content, user_uid=g.uid)
    s = Session()
    s.add(article)
    try: s.commit()
    except SQLAlchemyError: return { 'message': 'something wrong' }, 500
    finally: s.close()

    return { 'message': 'success' }

class Test(Resource):
  @login_required
  def get(self):
    s = Session()
    ars = s.query(Article.content, User.name).join(User, Article.user_uid==User.uid)
    s.close()
    return {'message': Article().rows_to_dict(ars) }
