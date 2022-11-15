
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

from sqlalchemy import func
from sqlalchemy.types import UserDefinedType

from sqlalchemy import func
from sqlalchemy.types import UserDefinedType, Float
class Point(UserDefinedType):

    def get_col_spec(self):
        return "POINT"

    def bind_expression(self,bindvalue ):
        return func.ST_PointFromText(bindvalue, type=self)

    def column_expression(self, col):
        return func.ST_AsText(col, type_=self)
    def bind_processor(self, dialect):
        def process(value):
            if value is None:
                return None
            assert isinstance(value, list)
            print(value)
            lat, lng = value
            return "POINT(%s %s)" % (lng, lat)
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is None:
                return None
            #m = re.match(r'^POINT\((\S+) (\S+)\)$', value)
            #lng, lat = m.groups()
            lng, lat = value[6:-1].split()  # 'POINT(135.00 35.00)' => ('135.00', '35.00')
            return (float(lat), float(lng))
        return process


class CellMeasurement(Base):
    __tablename__='CellMeasurement'
    id=Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True) 
    cell_id=Column(Integer, ForeignKey(Cell.id))
    participant_id=Column(Integer, ForeignKey(Participant.id))
    timestamp=Column(DateTime)
    measurement_type=Column(String)
    airdata_id=Column(Integer, ForeignKey(AirData.id), default=None)
    location=Column(Point)
    
    cells=relationship("Cell", back_populates="measurements")
    participants=relationship("Participant", back_populates="cellMeasurement")
    airdata_data=relationship("AirData",back_populates="cellMeasurement")
    # airData=relationship("AirData",back_populates="measurement")
   