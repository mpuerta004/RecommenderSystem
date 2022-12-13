
from sqlalchemy import (Column, DateTime, Float, ForeignKey,
                        Integer)
from sqlalchemy.orm import relationship
from sqlalchemy.types import Float
from db.base_class import Base
from models.Slot import Slot
from models.Measurement import Measurement
# sys.path.append("/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src")
# print(sys.path)
from models.Cell import Cell


class Priority(Base):
    __tablename__='Priority'
    timestamp=Column(DateTime, primary_key=True)
    slot_id=Column(Integer, ForeignKey(Slot.id),primary_key=True)
    temporal_priority=Column(Float) 
    trend_priority=Column(Float)
    
       
