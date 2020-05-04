from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Solution(Base):
    __tablename__ = 'solution'
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer)
    task_id = Column(Integer)


class Chat(Base):
    __tablename__ = 'chat'
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer)


class Question(Base):
    __tablename__ = 'question'
    id = Column(Integer, primary_key=True)
    statement = Column(String(5000))
    type = Column(String(30))
    correct_answer = Column(String(1000))
    announced = Column(Integer)
    start_time = Column(DateTime)
    announce_time = Column(DateTime)
    end_time = Column(DateTime)
    points = Column(Integer)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer)
    vk_id = Column(Integer)
    points = Column(Integer)
    admin = Column(Integer)


base_name = 'base.db'
engine = create_engine('sqlite:///{}?check_same_thread=False'.format(base_name))
session = sessionmaker()
session.configure(bind=engine)
session = session()
Base.metadata.create_all(engine)