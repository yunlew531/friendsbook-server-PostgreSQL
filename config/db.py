import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
import os

BASE = declarative_base()
print(2, os.getenv('DB_URL'))
engine = sqlalchemy.create_engine(os.getenv('DB_URL'))
Session = sqlalchemy.orm.sessionmaker(bind=engine)
s = Session()

BASE.metadata.create_all(engine)