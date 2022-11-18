from sqlalchemy import Integer, String, Column, DateTime, Boolean
from sqlalchemy.orm import relationship
from db.base_class import Base
from sqlalchemy import Integer, String, Column, DateTime, ForeignKey

from models.Cell import Cell

class Slot(Base):
    __tablaname__='Slot'
    id=Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True) 
    cell_id=Column(Integer, ForeignKey(Cell.id), primary_key=True,default=True)
    start_timestamp=Column(DateTime)
    end_timestamp=Column(DateTime)

    
    