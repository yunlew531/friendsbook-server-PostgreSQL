import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
import os

Base = declarative_base()

class BASE(Base):
  __abstract__ = True

  def to_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

engine = sqlalchemy.create_engine(os.getenv('DB_URL'))
Session = sqlalchemy.orm.sessionmaker(bind=engine)
s = Session()

BASE.metadata.create_all(engine)