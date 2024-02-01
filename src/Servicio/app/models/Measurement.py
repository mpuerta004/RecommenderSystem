
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime, ARRAY, Float
from sqlalchemy.orm import relationship

import sys
# sys.path.append("/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src")
from models.Cell import Cell
from db.base_class import Base
# from models.Reading import Reading
from models.Point import Point
from models.Member import Member
from models.Slot import Slot
from models.Device import Device
from models.Recommendation import Recommendation
from sqlalchemy import Integer, Enum, BigInteger

class Measurement(Base):
    __tablename__='Measurement'
    id=Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True) 
    member_id=Column(BigInteger, ForeignKey(Member.id, ondelete="CASCADE"))
    datetime=Column(DateTime)
    slot_id=Column(Integer, ForeignKey(Slot.id, ondelete="CASCADE"))
    location=Column(Point)
    device_id=Column(Integer,ForeignKey(Device.id,ondelete="CASCADE"))
    recommendation_id=Column(Integer,ForeignKey(Recommendation.id,ondelete="CASCADE"))
    co2=Column(Float)
    no2=Column(Float)
    so02=Column(Float)
    o3=Column(Float)
    so02=Column(Float)
    pm10=Column(Float)
    pm25=Column(Float)
    pm1=Column(Float)
    benzene=Column(Float)
    
    slot=relationship("Slot",cascade="all, delete")
    