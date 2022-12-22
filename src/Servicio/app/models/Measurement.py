
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime, ARRAY, Float
from sqlalchemy.orm import relationship
from geoalchemy2 import _DummyGeometry        
from geoalchemy2 import Geometry, WKTElement, Geography
import sys
# sys.path.append("/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src")
from models.Cell import Cell
from db.base_class import Base
from models.Reading import Reading
from models.Point import Point
from models.Member import Member
from models.Slot import Slot
from models.Device import Device

class Measurement(Base):
    __tablename__='Measurement'
    id=Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True) 
    cell_id=Column(Integer, ForeignKey(Cell.id, ondelete="CASCADE"))
    member_id=Column(Integer, ForeignKey(Member.id, ondelete="CASCADE"))
    timestamp=Column(DateTime)
    slot_id=Column(Integer, ForeignKey(Slot.id, ondelete="CASCADE"))
    measurement_type=Column(String)
    reading_id=Column(Integer, ForeignKey(Reading.id, ondelete="CASCADE"), nullable=True)
    location=Column(Point)
    device_id=Column(Integer,ForeignKey(Device.id,ondelete="CASCADE"))
    
    
    readings= relationship("Reading",cascade="all, delete")
    
    # member=relationship(Member)
    