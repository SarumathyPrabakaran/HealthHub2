import psycopg2

from sqlalchemy import Float, column, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from sqlalchemy.orm import relationship, backref
from datetime import datetime


from dotenv import load_dotenv
import os
load_dotenv() 

JSON_MIME_TYPE = 'application/json'

Base = declarative_base()

import mysql.connector

# Replace your PostgreSQL configuration with MySQL configuration
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

conn = mysql.connector.connect(
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT
)

print("Database connected successfully")
cur = conn.cursor()


def get_session():
    # Modify the SQLAlchemy connection string for MySQL
    engine = create_engine(f'mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    Base.metadata.create_all(engine)
    return session


class logincred(Base):
    __tablename__= "logincred"
    
    id          = Column(Integer, primary_key=True)
    email       = Column(String, nullable=False)
    password    = Column(String, nullable=False)
    
    
class Profiles(Base):
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('logincred.id'))
    profiles = Column(String)

class Activity(Base):
    __tablename__ = "activities"
    
    activity_id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profiles.id'))
    activity = Column(String)
    status = Column(Integer, default=0)
    date   = Column(Date)


class ActivityTracking(Base):
    __tablename__ = "activitytracking"
    
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    activity_id =Column(Integer, ForeignKey('activities.activity_id'))
    status = Column(Integer)
    


class Forum(Base):
    __tablename__ = "forum"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('logincred.id'))
    date = Column(Date,default=datetime.utcnow)
    content = Column(String(255))



session1 = get_session()