from flask import g
from flask_restful import Resource, request
from config.db import Session
from config.storage import storage
from uuid import uuid4
from sqlalchemy.exc import SQLAlchemyError
from decorator.login_required import login_required
from model.image import Image
from model.user import User

class ImageApi(Resource):
  # upload image
  @login_required
  def post(self):
    file = request.files.get('image-file')
    if not file.filename.endswith('.jpeg') and not file.filename.endswith('.jpg'):
      return { 'message': 'jpg or jpeg only', 'code': 1 }, 400
    uid = g.uid
    id = str(uuid4())

    # storage image to firebase storage
    ref = storage.child('{0}/{1}'.format(uid, id))
    ref.put(file)
    url = storage.child('{0}/{1}'.format(uid, id)).get_url(None)

    # storage image information to PostgreSQL
    image = Image(
      id=id,
      url=url,
      user_uid=g.uid,
    )

    s = Session()
    s.add(image)

    try: s.commit()
    except SQLAlchemyError: return { 'message': 'something wrong' }, 500
    finally: s.close()

    return { 'message': 'success', 'url': url }

  # delete image by image_id
  @login_required
  def delete(self, image_id):
    s = Session()
    image = s.query(Image).filter(Image.id==image_id).first()
    if not image: return { 'message': 'image not found' }, 404
    if image.user_uid != g.uid: return { 'message': 'permission denied' }, 403

    # PostgreSQL delete
    s.delete(image)

    # firebase storage delete
    ref = storage.child()
    ref.delete('{0}/{1}'.format(g.uid, image_id))

    try: s.commit()
    except SQLAlchemyError: return { 'message': 'something wrong' }, 500
    finally: s.close()

    return { 'message': 'success' }


class ImagesApi(Resource):
  def get(self, user_uid):
    s = Session()
    user = s.query(User).filter(User.uid==user_uid).first()
    if not user: return { 'message': 'user not found' }, 404

    image_query = s.query(Image).filter(Image.user_uid==user_uid)
    s.close()
    images = []
    for image in image_query:
      images.append(image.query_to_dict())

    return { 'message': 'success', 'images': images }

class BannerImgApi(Resource):
  # upload banner image by jwt token uid
  @login_required
  def post(self):
    file = request.files.get('image-file')
    if not file.filename.endswith('.jpeg') and not file.filename.endswith('.jpg'):
      return { 'message': 'jpg or jpeg only', 'code': 1 }, 400
    uid = g.uid
    id = str(uuid4())

    # storage image to firebase storage
    ref = storage.child('{0}/{1}'.format(uid, id))
    ref.put(file)
    url = storage.child('{0}/{1}'.format(uid, id)).get_url(None)

    s = Session()

    # storage image information to PostgreSQL
    image = Image(
      id=id,
      url=url,
      user_uid=g.uid,
    )
    s.add(image)

    # set banner_url to user profile
    user = s.query(User).filter(User.uid==g.uid).first()
    if not user: return {'message': 'user not found' }, 404

    user.banner_url = url

    try: s.commit()
    except SQLAlchemyError: return { 'message': 'something wrong' }, 500
    finally: s.close()

    return { 'message': 'success', 'url': url }

class AvatarImgApi(Resource):
  # upload avatar image by jwt token uid
  @login_required
  def post(self):
    file = request.files.get('image-file')
    if not file.filename.endswith('.jpeg') and not file.filename.endswith('.jpg'):
      return { 'message': 'jpg or jpeg only', 'code': 1 }, 400
    uid = g.uid
    id = str(uuid4())

    # storage image to firebase storage
    ref = storage.child('{0}/{1}'.format(uid, id))
    ref.put(file)
    url = storage.child('{0}/{1}'.format(uid, id)).get_url(None)

    s = Session()

    # storage image information to PostgreSQL
    image = Image(
      id=id,
      url=url,
      user_uid=g.uid,
    )
    s.add(image)

    # set banner_url to user profile
    user = s.query(User).filter(User.uid==g.uid).first()
    if not user: return {'message': 'user not found' }, 404

    user.avatar_url = url

    try: s.commit()
    except SQLAlchemyError: return { 'message': 'something wrong' }, 500
    finally: s.close()

    return { 'message': 'success', 'url': url }