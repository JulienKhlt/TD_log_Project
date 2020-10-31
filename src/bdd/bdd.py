from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = 'mysql+pymysql://tdlog:tdlog@localhost:3333/autocomplete'
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()

