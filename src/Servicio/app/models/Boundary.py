
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship


from db.base_class import Base
from models.Point import Point

from models.Surface import Surface


class Boundary(Base):
    __tablename__='Boundary'
    id=Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True) 
    surface_id=Column(Integer,ForeignKey(Surface.id, ondelete="CASCADE"),  primary_key=True)
    center=Column(Point)
    rad=Column(Integer)
    
    
    # cells = relationship("Cell")

    #De este modo se define una relacion inversa... no se si seran utiles. 
    #queenBee=relationship("Campaign", back_populates="campaigns")
    

