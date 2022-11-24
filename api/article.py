from flask import g
from flask_restful import Resource, request
from config.db import Session
from sqlalchemy.exc import SQLAlchemyError
from decorator.login_required import login_required
from model.article import Article, Comment, ArticleLike
from model.user import User

class ArticleApi(Resource):
  # get personal page articles by token
  # include fan article, club article
  @login_required
  def get(self):
    s = Session()

    # article join author
    articles_rows = s.query(Article, User.name, User.avatar_url).join(
      User, Article.user_uid==User.uid
    ).filter(Article.user_uid==g.uid)

    articles_list = []
    for article_row in articles_rows:
      result_group = article_row._asdict()
      article_dict = result_group.get('Article').query_to_dict()
      article_id = article_dict.get('id')

      # article join article_likes
      article_likes_rows = s.query(ArticleLike, User.name, User.uid, User.avatar_url).join(
        User, ArticleLike.user_uid==User.uid
      ).filter(ArticleLike.article_id==article_id)

      article_likes_list = []
      for article_likes_row in article_likes_rows:
        article_likes_result = article_likes_row._asdict()
        article_likes_dict = article_likes_result.get('ArticleLike').query_to_dict()
        article_likes_list.append({
          **article_likes_dict,
          'author': {
            'uid': article_likes_result.get('uid'),
            'name': article_likes_result.get('name'),
            'avatar_url': article_likes_result.get('avatar_url')
          }
        })

      # article join comments
      comment_rows = s.query(Comment, User.name, User.uid, User.avatar_url).join(
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
            'name': comment_result_group.get('name'),
            'avatar_url': comment_result_group.get('avatar_url')
          },
        })

      articles_list.append({
        **article_dict,
        'author': {
          'name': result_group.get('name'),
          'uid': g.uid,
          'avatar_url': result_group.get('avatar_url')
        },
        'comments': comments_list,
        'article_likes': article_likes_list
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

    article_likes = s.query(ArticleLike).filter(ArticleLike.article_id==article_id)
    for article_like in article_likes:
      s.delete(article_like)

    s.delete(article)

    try: s.commit()
    except SQLAlchemyError: return { 'message': 'something wrong' }, 500
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

    comment_rows = s.query(Comment, User.name, User.uid, User.avatar_url).join(
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
          'name': result.get('name'),
          'avatar_url': result.get('avatar_url'),
        }
      })

    return { 'message': 'success', 'comments': comment_list }

class ArticleLikeApi(Resource):
  # get article_likes by article id
  def get(self, article_id):
    s = Session()
    article = s.query(Article).filter(Article.id==article_id).first()
    if not article: return { 'message': 'article not found' }, 404

    article_likes_rows = s.query(ArticleLike, User.name, User.uid, User.avatar_url).join(
      User, ArticleLike.user_uid==User.uid
    ).filter(ArticleLike.article_id==article_id)

    article_likes_list = []
    for article_likes_row in article_likes_rows:
      article_likes_result = article_likes_row._asdict()
      article_likes_dict = {
        **article_likes_result.get('ArticleLike').query_to_dict(),
        'author': {
          'uid': article_likes_result.get('uid'),
          'name': article_likes_result.get('name'),
          'avatar_url': article_likes_result.get('avatar_url'),
        }
      }
      article_likes_list.append(article_likes_dict)

    return { 'message': 'success', 'article_likes': article_likes_list }

  # thumbs up article
  @login_required
  def post(self, article_id):
    s = Session()
    article = s.query(Article).filter(Article.id==article_id).first()
    if not article: return { 'message': 'article not found' }, 404
    article_like_exist = s.query(ArticleLike).filter(ArticleLike.article_id==article_id).filter(ArticleLike.user_uid==g.uid).first()
    
    if article_like_exist: 
      s.delete(article_like_exist)
    else:
      article_like = ArticleLike()
      article_like.user_uid = g.uid
      article_like.article_id = article_id
      s.add(article_like)

    try: s.commit()
    except SQLAlchemyError: return { 'message': 'something wrong' }, 500
    finally: s.close()

    return { 'message': 'success' }, 200

class ArticlesByUidApi(Resource):
  def get(self, user_uid):
    s = Session()
    user = s.query(User).filter(User.uid==user_uid).first()
    if not user: return { 'message': 'user not found' }, 404
    
    # article join author
    articles_rows = s.query(Article, User.name, User.avatar_url).join(
      User, Article.user_uid==User.uid
    ).filter(Article.user_uid==user_uid)

    articles_list = []
    for article_row in articles_rows:
      result_group = article_row._asdict()
      article_dict = result_group.get('Article').query_to_dict()
      article_id = article_dict.get('id')

      # article join article_likes
      article_likes_rows = s.query(ArticleLike, User.name, User.uid, User.avatar_url).join(
        User, ArticleLike.user_uid==User.uid
      ).filter(ArticleLike.article_id==article_id)

      article_likes_list = []
      for article_likes_row in article_likes_rows:
        article_likes_result = article_likes_row._asdict()
        article_likes_dict = article_likes_result.get('ArticleLike').query_to_dict()
        article_likes_list.append({
          **article_likes_dict,
          'author': {
            'uid': article_likes_result.get('uid'),
            'name': article_likes_result.get('name'),
            'avatar_url': article_likes_result.get('avatar_url')
          }
        })

      # article join comments
      comment_rows = s.query(Comment, User.name, User.uid, User.avatar_url).join(
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
            'name': comment_result_group.get('name'),
            'avatar_url': comment_result_group.get('avatar_url')
          },
        })

      articles_list.append({
        **article_dict,
        'author': {
          'name': result_group.get('name'),
          'uid': user_uid,
          'avatar_url': result_group.get('avatar_url'),
        },
        'comments': comments_list,
        'article_likes': article_likes_list
      })
    s.close()

    return { 'message': 'success', 'articles': articles_list }