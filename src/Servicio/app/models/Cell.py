
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime, ARRAY, Float
from sqlalchemy.orm import relationship
from geoalchemy2 import _DummyGeometry        
from geoalchemy2 import Geometry, WKTElement, Geography
import sys
# sys.path.append("/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src")
# print(sys.path)

from db.base_class import Base

from  models.Surface import Surface

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


class Cell(Base):
    __tablename__='Cell'
    id=Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True) 
    surface_id=Column(Integer,ForeignKey(Surface.id))
    inferior_coord= Column(Point, nullable=False)
    # inferior_coord=Column(Geography(geometry_type='POINT', srid=4326))
    # Column(ARRAY(Float))#Column(Geometry('POINT'),default=None)
    #superior_coord=Column(Geometry('POINT'),default=None)
    cell_type=Column(String, default="Dynamic")
    #center=Column(Geometry('POINT'),default=None)
    
    surfaces_cells=relationship("Surface", back_populates="cells")
    #De este modo se define una relacion inversa... no se si seran utiles. 
    #queenBee=relationship("Campaign", back_populates="campaigns")
    

 
if __name__ == "__main__":
    geo = Cell(id=100,inferior_coord='POINT(40.7647919738352, -73.99207372979897)')
    print(geo.inferior_coord)
