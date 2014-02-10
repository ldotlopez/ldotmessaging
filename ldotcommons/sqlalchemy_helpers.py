from sqlalchemy import create_engine as sqlalchemy_create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def create_engine(dbpath='sqlite:///:memory:', echo=False):
    engine = sqlalchemy_create_engine(dbpath, echo=echo)
    Base.metadata.create_all(engine)
    return engine

def create_session(dbpath=None, engine=None, echo=False):
    if not engine:
        engine = create_engine(dbpath, echo)
    Session = sessionmaker(bind=engine)
    return Session()
