from sqlalchemy import create_engine as sqlalchemy_create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

"""
store.py file must use the create_engine and create_session to implement
a wrapper like this:

def create_session():
    def create_engine():
        engine = db.create_engine(dbpath=dbpath)
        _Base.metadata.create_all(engine)
        return engine

    return db.create_session(engine=create_engine())
"""

Base = declarative_base()

def create_engine(dbpath='sqlite:///:memory:', echo=False):
    """
    Dont use directly, write a wrapper over this in your store.py file
    """
    engine = sqlalchemy_create_engine(dbpath, echo=echo)
    Base.metadata.create_all(engine)
    return engine

def create_session(dbpath=None, engine=None, echo=False):
    """
    Dont use directly, write a wrapper over this in your store.py file
    """
    if not engine:
        engine = create_engine(dbpath, echo)
    Session = sessionmaker(bind=engine)
    return Session()
