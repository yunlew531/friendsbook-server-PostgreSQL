from flask import g
from flask_restful import Resource, request
from config.db import Session
from model.article import Article
from decorator.login_required import login_required
import json

class ArticleApi(Resource):
  @login_required
  def get(self):
    s = Session()
    articles_query = s.query(Article).filter(Article.user_uid==g.uid)
    articles_list = []
    for article in articles_query: articles_list.append(article.query_to_dict())
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
    except Exception as e: 
      print(e)
      return { 'message': 'something wrong' }, 500
    finally: s.close()

    return { 'message': 'success' }
