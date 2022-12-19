
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
from models.Campaign import Campaign
from models.Slot import Slot


class Measurement(Base):
    __tablename__='Measurement'
    id=Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True) 
    cell_id=Column(Integer, ForeignKey(Cell.id))
    member_id=Column(Integer, ForeignKey(Member.id))
    timestamp=Column(DateTime)
    slot_id=Column(Integer, ForeignKey(Slot.id),)
    measurement_type=Column(String)
    airdata_id=Column(Integer, ForeignKey(Reading.id), nullable=True)
    location=Column(Point)
    # campaign_id=Column(Integer, ForeignKey(Campaign.id))
    
    airData= relationship("Reading")
    
    # member=relationship(Member)
    