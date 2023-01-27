
from sqlalchemy import (Column, String, DateTime, Float, ForeignKey,
                        Integer)
from sqlalchemy.orm import relationship
from sqlalchemy.types import Float
from db.base_class import Base
# sys.path.append("/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src")
# print(sys.path)
from models.Hive import Hive
from models.Member import Member
from sqlalchemy import Integer, Enum



class HiveMember(Base):
    __tablename__='HiveMember'
    hive_id=Column(Integer, ForeignKey(Hive.id, ondelete="CASCADE"),primary_key=True)
    member_id=Column(Integer, ForeignKey(Member.id, ondelete="CASCADE"),primary_key=True)
    role=Column(Enum("WorkerBee","QueenBee","DroneBee" ),primary_key=True,default="WorkerBee")
       
    member=relationship("Member",cascade="all, delete")