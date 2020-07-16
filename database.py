from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session,sessionmaker
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg2://testDatabaseUser:ce*O[]~8d7qewqL!N@localhost/testDatabase")

db_Session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)
