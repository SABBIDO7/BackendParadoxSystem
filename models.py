from sqlalchemy import Integer,String,Column,DateTime,ForeignKey,Double
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
Base=declarative_base()


# Define your models
class CompanyManagementP(Base):
    __tablename__ = 'GeneralInformation'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    tel = Column(String)
    currency = Column(String)
    #employees = relationship('Employee', back_populates='company')

class UsersP(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    department_id = Column(Integer, ForeignKey('departments.id'))
    department = relationship('DepartmentsP', back_populates='users')
    
class DepartmentsP(Base):
    __tablename__='departments'
    id=Column(Integer,primary_key=True,index=True)
    name=Column(String(100),unique=True)
    description=Column(String(100))
    users=relationship('UsersP',back_populates='department')
