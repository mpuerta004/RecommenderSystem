from sqlalchemy import Integer, String, Column, Boolean, ForeignKey,Boolean,DateTime
from sqlalchemy.orm import relationship
from db.base_class import Base
from sqlalchemy import Integer, Enum


class Member(Base):
    __tablename__='Member'
    mail=Column(String, nullable=False)
    id=Column(Integer, primary_key=True, index=True, unique=True,  autoincrement=True, nullable=False)
    name=Column(String,nullable=True)
    age=Column(Integer,nullable=True)
    surname=Column(String,nullable=True)
    birthday=Column(DateTime)
    city=Column(String,nullable=True)
    gender=Column(Enum("NOBINARY","MALE","FEMALE",'NOANSER'),nullable=False)
    real_user=Column(Boolean,default=True)
    
    
    
    # device_id=Column(Integer,ForeignKey(Device.id, ondelete='CASCADE'))
    
    #Measurements=relationship("Measurement",cascade="all, delete")
    # hives=relationship("Hive_Member", cascade="all, delete")
    # campaign_creator= relationship("Campaign",cascade="all, delete")

    