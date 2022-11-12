import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
import os

Base = declarative_base()

class BASE(Base):
  __abstract__ = True

  def query_to_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

  @staticmethod
  def row_to_dict(sqlalchemy_row, select_columns_list):
    return {select_columns_list[i]: column for i, column in enumerate(sqlalchemy_row)}

# connect to database
engine = sqlalchemy.create_engine(os.getenv('DB_URL'))
Session = sqlalchemy.orm.sessionmaker(bind=engine)
BASE.metadata.create_all(engine)