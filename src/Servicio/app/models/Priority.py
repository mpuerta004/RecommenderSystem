
from sqlalchemy import (Column, DateTime, Float, ForeignKey,
                        Integer)
from sqlalchemy.orm import relationship
from sqlalchemy.types import Float
from db.base_class import Base
from models.Slot import Slot


class Priority(Base):
    __tablename__='Priority'
    datetime=Column(DateTime, primary_key=True)
    slot_id=Column(Integer, ForeignKey(Slot.id, ondelete="CASCADE"),primary_key=True)
    temporal_priority=Column(Float) 
    trend_priority=Column(Float)
    
       
