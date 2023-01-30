
from sqlalchemy import Integer, String, Column, ForeignKey
from sqlalchemy.orm import relationship
from db.base_class import Base
from models.Surface import Surface
from models.Point import Point



class Cell(Base):
    __tablename__ = 'Cell'
    id = Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True)
 
    centre = Column(Point)
    radius=Column(Integer,default=1)
    cell_type = Column(String, default="Dynamic")
    surface_id = Column(Integer, ForeignKey(Surface.id, ondelete="CASCADE"))

   