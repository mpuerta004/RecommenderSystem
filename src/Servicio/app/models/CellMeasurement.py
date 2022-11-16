
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime, ARRAY, Float
from sqlalchemy.orm import relationship
from geoalchemy2 import _DummyGeometry        
from geoalchemy2 import Geometry, WKTElement, Geography
import sys
# sys.path.append("/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src")
# print(sys.path)
from models.Participant import Participant
from models.Cell import Cell
from db.base_class import Base
from models.AirData import AirData
from models.Point import Point

class CellMeasurement(Base):
    __tablename__='CellMeasurement'
    id=Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True) 
    cell_id=Column(Integer, ForeignKey(Cell.id))
    participant_id=Column(Integer, ForeignKey(Participant.id))
    timestamp=Column(DateTime)
    measurement_type=Column(String)
    airdata_id=Column(Integer, ForeignKey(AirData.id), default=None)
    location=Column(Point)
    
    airData= relationship("AirData", back_populates="cellMeasurement")
