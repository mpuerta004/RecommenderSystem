
from sqlalchemy import (Column, String, DateTime, Float, ForeignKey,
                        Integer)
from sqlalchemy.orm import relationship
from db.base_class import Base

from models.Hive import Hive
from models.Member import Member
from sqlalchemy import Integer, Enum
from sqlalchemy import Integer, Enum, BigInteger



class Hive_Member(Base):
    __tablename__='Hive_Member'
    hive_id=Column(Integer, ForeignKey(Hive.id, ondelete="CASCADE"),primary_key=True)
    member_id=Column(BigInteger, ForeignKey(Member.id, ondelete="CASCADE"),primary_key=True)
    role=Column(Enum("WorkerBee","QueenBee","DroneBee" ),primary_key=True,default="WorkerBee")
       
    member=relationship("Member")