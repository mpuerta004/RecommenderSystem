from sqlalchemy import Integer, String, Column, DateTime, Boolean
from sqlalchemy.orm import relationship
from db.base_class import Base
from sqlalchemy import Integer, String, Column, DateTime, ForeignKey

from models.Cell import Cell

class Slot(Base):
    __tablaname__='Slot'
    id=Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True) 
    cell_id=Column(Integer, ForeignKey(Cell.id, ondelete="CASCADE"), primary_key=True,default=True)
    start_datetime=Column(DateTime)
    end_datetime=Column(DateTime)
    
    cell=relationship("Cell")
   