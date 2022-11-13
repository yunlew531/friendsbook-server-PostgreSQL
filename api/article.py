from decimal import Decimal
from flask import g
from flask_restful import Resource, request
from config.db import Session
from sqlalchemy.exc import SQLAlchemyError
from decorator.login_required import login_required
from model.article import Article, Comment
from model.user import User

class ArticleApi(Resource):
  @login_required
  # get personal page article
  def get(self):
    s = Session()
    articles_rows = s.query(Article, User.name).join(
      User, Article.user_uid==User.uid
    ).filter(Article.user_uid==g.uid)
    articles_list = []
    for article_row in articles_rows:
      result_group = article_row._asdict()
      article_dict = result_group.get('Article').query_to_dict()
      article_id = article_dict.get('id')

      # article join comments
      comment_rows = s.query(Comment, User.name, User.uid).join(
        User, Comment.user_uid==User.uid
      ).filter(Comment.article_id==article_id)
      comments_list = []
      for comment_row in comment_rows:
        result_group = comment_row._asdict()
        comment_dict = result_group.get('Comment').query_to_dict()
        comments_list.append({
          **comment_dict,
          'author': {
            'uid': result_group.get('uid'),
            'name': result_group.get('name')
          },
          'created_at': 0,
        })
      articles_list.append({
        **article_dict,
        'author': {
          'name': result_group.get('name'),
          'uid': g.uid
        },
        'comments': comments_list
      })
    s.close()

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

class CommentApi(Resource):
  @login_required
  def post(self, article_id):
    # post comment in article
    body = request.get_json()
    content = body.get('content')

    if not content: return { 'message': 'content required' }, 400
    
    comment = Comment(
      content=content,
      article_id=article_id,
      user_uid=g.uid
    )

    s = Session()
    s.add(comment)

    try: s.commit()
    except SQLAlchemyError: { 'message': 'something wrong' }, 500
    finally: s.close()

    return { 'message':'success' }