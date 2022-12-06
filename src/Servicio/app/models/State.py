from sqlalchemy import Integer, String, Column, DateTime, Boolean
from sqlalchemy.orm import relationship
from db.base_class import Base


class State(Base):
    __tablaname__='State'
    id=Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True) 
    state=Column(String,nullable=False, default="created")
    initiative_human=Column(Boolean,default=False)
    timestamp_update=Column(DateTime)

    
    