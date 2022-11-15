
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime, ARRAY, Float
from sqlalchemy.orm import relationship
from geoalchemy2 import _DummyGeometry        
from geoalchemy2 import Geometry, WKTElement, Geography
import sys
# sys.path.append("/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src")
# print(sys.path)
from models.Participant import Participant
from db.base_class import Base

from  models.Surface import Surface

from sqlalchemy import func
from sqlalchemy.types import UserDefinedType

from sqlalchemy import func
from sqlalchemy.types import UserDefinedType, Float


class AirData(Base):
    __tablename__='AirData'
    id=Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True) 
    Co2=Column(Float)
    No2=Column(Float)
    
    cellMeasurement= relationship("CellMeasurement",back_populates="airdata_data")

    # cellMeasurement_id=Column(Integer, ForeignKey(CellMeasurement.id))
    

    
    # surfaces_cells=relationship("Surface", back_populates="cells")