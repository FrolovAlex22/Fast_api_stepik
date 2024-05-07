from datetime import datetime
from sqlalchemy import JSON, MetaData, Integer, String, TIMESTAMP, ForeignKey, Table, Column
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Roles(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    permissions = Column(JSON)


class User(Base):
    __tablename__ = 'users'
    id = Column('id', Integer, primary_key=True)
    email = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    registered_ad = Column(TIMESTAMP, default=datetime.utcnow),
    role_id = Column(Integer, ForeignKey('roles.id'))


class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    count = Column(Integer, nullable=False)
