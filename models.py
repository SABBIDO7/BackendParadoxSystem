from sqlalchemy import Integer,String,Column,DateTime,ForeignKey,Double
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
Base=declarative_base()
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Create a Base class
Base = declarative_base()
# Define your models
class Company(Base):
    __tablename__ = 'company'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    tel = Column(String(100))
    currency = Column(String(100))

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100))
    password = Column(String(200))
    user_control = Column((String(100)))
    email = Column(String(100))
    sales = Column(String(100))
    sales_return = Column(String(100))
    purshase = Column(String(100))
    purshase_return = Column(String(100))
    order = Column(String(100))
    trans = Column(String(100))
    items = Column(String(100))
    chart = Column(String(100))
    statement = Column(String(100))

class Departments(Base):
    __tablename__='departments'
    id=Column(Integer,primary_key=True,index=True)
    name=Column(String(100),unique=True)
    description=Column(String(100))

class Currencies(Base):
    __tablename__='currencies'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)

class Stations(Base):
    __tablename__='stations'
    id = Column(Integer, primary_key=True, index=True)
    pcname = Column(String(100), unique=True)
    pcid = Column(String(100), unique=True)

