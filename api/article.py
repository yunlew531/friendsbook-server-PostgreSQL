from flask import g
from flask_restful import Resource, request
from config.db import Session
from sqlalchemy.exc import SQLAlchemyError
from decorator.login_required import login_required
from model.article import Article, Comment, ArticleThumbsUp
from model.user import User

class ArticleApi(Resource):
  # get personal page articles by token
  # include fan article, club article
  @login_required
  def get(self):
    s = Session()

    # article join author
    articles_rows = s.query(Article, User.name).join(
      User, Article.user_uid==User.uid
    ).filter(Article.user_uid==g.uid)

    articles_list = []
    for article_row in articles_rows:
      result_group = article_row._asdict()
      article_dict = result_group.get('Article').query_to_dict()
      article_id = article_dict.get('id')

      # article join thumbs_up
      thumbs_up_rows = s.query(ArticleThumbsUp, User.name, User.uid).join(
        User, ArticleThumbsUp.user_uid==User.uid
      ).filter(ArticleThumbsUp.article_id==article_id)

      thumbs_up_list = []
      for thumbs_up_row in thumbs_up_rows:
        thumbs_up_result = thumbs_up_row._asdict()
        thumbs_up_dict = thumbs_up_result.get('ArticleThumbsUp').query_to_dict()
        thumbs_up_list.append({
          **thumbs_up_dict,
          'author': {
            'uid': thumbs_up_result.get('uid'),
            'name': thumbs_up_result.get('name')
          }
        })

      # article join comments
      comment_rows = s.query(Comment, User.name, User.uid).join(
        User, Comment.user_uid==User.uid
      ).filter(Comment.article_id==article_id)

      comments_list = []
      for comment_row in comment_rows:
        comment_result_group = comment_row._asdict()
        comment_dict = comment_result_group.get('Comment').query_to_dict()
        comments_list.append({
          **comment_dict,
          'author': {
            'uid': comment_result_group.get('uid'),
            'name': comment_result_group.get('name')
          },
        })

      articles_list.append({
        **article_dict,
        'author': {
          'name': result_group.get('name'),
          'uid': g.uid
        },
        'comments': comments_list,
        'thumbs_up': thumbs_up_list
      })
    s.close()

    return { 'message': 'success', 'articles': articles_list }

  # post article on personal page
  @login_required
  def post(self):
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
  
  # delete article
  @login_required
  def delete(self, article_id):
    s = Session()
    article = s.query(Article).filter(Article.id==article_id).first()
    if not article: return { 'message': 'article not found' }, 404
    if article.user_uid != g.uid: return { 'message': 'permission denied' }, 403

    comments = s.query(Comment).filter(Comment.article_id==article_id)
    for comment in comments:
      s.delete(comment)

    thumbs_up = s.query(ArticleThumbsUp).filter(ArticleThumbsUp.article_id==article_id)
    for thumb in thumbs_up:
      s.delete(thumb)

    s.delete(article)

    try: s.commit()
    except SQLAlchemyError as e : 
      print(e) 
      return { 'message': 'something wrong' }, 500
      
    finally: s.close()

    return { 'message': 'success' }

class CommentApi(Resource):
  # post comment in article
  @login_required
  def post(self, article_id):
    body = request.get_json()
    content = body.get('content')
    if type(content) == str: content = content.rstrip()

    if not content: return { 'message': 'content required', 'code': 1 }, 400
    if len(content) > 300: return { 'message': 'content too long', 'code': 2 }, 400
    
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

class CommentsApi(Resource):
  # get comments by article_id
  @login_required
  def get(self, article_id):
    s = Session()
    article = s.query(Article).filter(Article.id==article_id).first()
    if not article: return { 'message':'article not found' }, 404

    comment_rows = s.query(Comment, User.name, User.uid).join(
      User, Comment.user_uid==User.uid
    ).filter(Comment.article_id==article_id)
    s.close()

    comment_list = []
    for comment_row in comment_rows:
      result = comment_row._asdict()
      comment_query = result.get('Comment')
      comment_list.append({
        **comment_query.query_to_dict(),
        'author': {
          'uid': result.get('uid'),
          'name': result.get('name')
        }
      })

    return { 'message': 'success', 'comments': comment_list }

class ArticleThumbsUpApi(Resource):
  # get thumbs_up by article id
  def get(self, article_id):
    s = Session()
    article = s.query(Article).filter(Article.id==article_id).first()
    if not article: return { 'message': 'article not found' }, 404

    thumbs_up_rows = s.query(ArticleThumbsUp, User.name, User.uid).join(
      User, ArticleThumbsUp.user_uid==User.uid
    ).filter(ArticleThumbsUp.article_id==article_id)

    thumbs_up_list = []
    for thumbs_up_row in thumbs_up_rows:
      thumbs_up_result = thumbs_up_row._asdict()
      thumbs_up_dict = {
        **thumbs_up_result.get('ArticleThumbsUp').query_to_dict(),
        'author': {
          'uid': thumbs_up_result.get('uid'),
          'name': thumbs_up_result.get('name')
        }
      }
      thumbs_up_list.append(thumbs_up_dict)

    return { 'message': 'success', 'thumbs_up': thumbs_up_list }

  # thumbs up article
  @login_required
  def post(self, article_id):
    s = Session()
    article = s.query(Article).filter(Article.id==article_id).first()
    if not article: return { 'message': 'article not found' }, 404
    thumbs_up_exist = s.query(ArticleThumbsUp).filter(ArticleThumbsUp.article_id==article_id).filter(ArticleThumbsUp.user_uid==g.uid).first()
    
    if thumbs_up_exist: 
      s.delete(thumbs_up_exist)
    else:
      thumbs_up = ArticleThumbsUp()
      thumbs_up.user_uid = g.uid
      thumbs_up.article_id = article_id
      s.add(thumbs_up)

    try: s.commit()
    except SQLAlchemyError: return { 'message': 'something wrong' }, 500
    finally: s.close()

    return { 'message': 'success' }, 200

class ArticlesByUid(Resource):
  def get(self, user_uid):
    s = Session()
    user = s.query(User).filter(User.uid==user_uid).first()
    if not user: return { 'message': 'user not found' }, 404
    
    # article join author
    articles_rows = s.query(Article, User.name).join(
      User, Article.user_uid==User.uid
    ).filter(Article.user_uid==user_uid)

    articles_list = []
    for article_row in articles_rows:
      result_group = article_row._asdict()
      article_dict = result_group.get('Article').query_to_dict()
      article_id = article_dict.get('id')

      # article join thumbs_up
      thumbs_up_rows = s.query(ArticleThumbsUp, User.name, User.uid).join(
        User, ArticleThumbsUp.user_uid==User.uid
      ).filter(ArticleThumbsUp.article_id==article_id)

      thumbs_up_list = []
      for thumbs_up_row in thumbs_up_rows:
        thumbs_up_result = thumbs_up_row._asdict()
        thumbs_up_dict = thumbs_up_result.get('ArticleThumbsUp').query_to_dict()
        thumbs_up_list.append({
          **thumbs_up_dict,
          'author': {
            'uid': thumbs_up_result.get('uid'),
            'name': thumbs_up_result.get('name')
          }
        })

      # article join comments
      comment_rows = s.query(Comment, User.name, User.uid).join(
        User, Comment.user_uid==User.uid
      ).filter(Comment.article_id==article_id)

      comments_list = []
      for comment_row in comment_rows:
        comment_result_group = comment_row._asdict()
        comment_dict = comment_result_group.get('Comment').query_to_dict()
        comments_list.append({
          **comment_dict,
          'author': {
            'uid': comment_result_group.get('uid'),
            'name': comment_result_group.get('name')
          },
        })

      articles_list.append({
        **article_dict,
        'author': {
          'name': result_group.get('name'),
          'uid': user_uid
        },
        'comments': comments_list,
        'thumbs_up': thumbs_up_list
      })
    s.close()

    return { 'message': 'success', 'articles': articles_list }