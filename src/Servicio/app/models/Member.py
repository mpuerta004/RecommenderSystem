from sqlalchemy import Integer, String, Column, Boolean, ForeignKey,Boolean,DateTime
from sqlalchemy.orm import relationship
from db.base_class import Base
from sqlalchemy import Integer, Enum, BigInteger


class Member(Base):
    __tablename__='Member'
    mail=Column(String, nullable=False)
    id=Column(BigInteger, primary_key=True, index=True, unique=True,  nullable=False)
    name=Column(String,nullable=True)
    age=Column(Integer,nullable=True)
    surname=Column(String,nullable=True)
    birthday=Column(DateTime)
    city=Column(String,nullable=True)
    gender=Column(Enum("NOBINARY","MALE","FEMALE",'NOANSWER'),nullable=False)
    real_user=Column(Boolean,default=True)
    
    
    