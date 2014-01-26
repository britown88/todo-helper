import os
from sqlalchemy import create_engine
from sqlalchemy import Table, Boolean, Column, Integer, String, Text, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

sqliteConnectionString = 'sqlite:///%s' % os.path.join(PROJECT_DIR, '..', '..', 'derp.db')
engine = create_engine(sqliteConnectionString, echo=True)
Base = declarative_base(bind=engine)
Session = scoped_session(sessionmaker(engine))


class Derp(Base):
    __tablename__ = 'derp'

    id = Column(Integer, primary_key=True)
    key = Column(String(80), index=True, unique=True)
    value = Column(String(256), unique=False)

    def __repr__(self):
        return '<Derp %s/%s/>' % (self.key, self.value)

Base.metadata.create_all()
