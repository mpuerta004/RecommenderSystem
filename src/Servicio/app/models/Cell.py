
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import Column
from geoalchemy2 import Geometry

from db.base_class import Base

from models.Surface import Surface



class Cell(Base):
    __tablename__='Cell'
    id=Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True) 
    surface_id=Column(Integer,ForeignKey(Surface.id))
    #inferior_coord=Column(Geometry('POINT'),default=None)
    #superior_coord=Column(Geometry('POINT'),default=None)
    cell_type=Column(String, default="Dynamic")
    #center=Column(Geometry('POINT'),default=None)
    surfaces_cells=relationship("Surface", back_populates="cells")
    #De este modo se define una relacion inversa... no se si seran utiles. 
    #queenBee=relationship("Campaign", back_populates="campaigns")
    

