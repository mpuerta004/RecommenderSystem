
from sqlalchemy import Integer, String,Float, Column, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship


from db.base_class import Base
from models.Point import Point



class Boundary(Base):
    __tablename__='Boundary'
    id=Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True) 
    centre=Column(Point)
    radius=Column(Float)
    
    
  

