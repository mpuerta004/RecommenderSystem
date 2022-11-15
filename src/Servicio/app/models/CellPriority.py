
import sys

from db.base_class import Base
from geoalchemy2 import Geography, Geometry, WKTElement, _DummyGeometry
from models.AirData import AirData
from models.Cell import Cell
from models.CellMeasurement import CellMeasurement
# sys.path.append("/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src")
# print(sys.path)
from models.Participant import Participant
from sqlalchemy import (ARRAY, Boolean, Column, DateTime, Float, ForeignKey,
                        Integer, String, func)
from sqlalchemy.orm import relationship
from sqlalchemy.types import Float, UserDefinedType


class CellPriority(Base):
    __tablename__='CellPriority'
    cellMeasurement_id=Column(Integer, ForeignKey(CellMeasurement.id), nullable=True)
    timestamp=Column(DateTime, primary_key=True)
    cell_id=Column(Integer, ForeignKey(Cell.id),primary_key=True)

    temporal_priority=Column(Float) 
    trend_priority=Column(Float)
    
    cell=relationship("Cell", back_populates="priority")
    # cellMeasurements=relationship("CellMeasurement",back_populates="priority")
    
   
   