from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Unicode, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine('sqlite:///linky_engine.db')
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)


class user_register(Base):
    __tablename__ = 'user_registered'

    def __init__(self, email, send_key, create_time, last_login):
        self.email = email
        self.send_key = send_key
        self.create_time = create_time
        self.last_login = last_login

    id = Column('id', Integer, primary_key=True)
    email = Column('email', Unicode(60), unique=True, nullable=False)
    send_key = Column('send_key', Unicode(30), nullable=False)
    create_time = Column('created_time', DateTime)
    last_login = Column('last_login', DateTime, default=datetime.utcnow)


class user_verified(Base):
    __tablename__ = 'user_verified'

    id = Column('id', Integer, primary_key=True)
    email = Column('email', Unicode(60), unique=True, nullable=False)
    email_key = Column('email_key', Unicode(50), nullable=False)


class emails_sent(Base):
    __tablename__ = 'emails_sent'

    id = Column('id', Integer, primary_key=True)
    email = Column('email', ForeignKey('user_verified.email'),
                   unique=True, nullable=False)
    email_key = Column('email_key', ForeignKey('user_verified.email_key'),
                       nullable=False)
    num_sent = Column('num_sent', Integer)


def create_db():
    Base.metadata.create_all()