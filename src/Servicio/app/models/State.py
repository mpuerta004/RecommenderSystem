from sqlalchemy import Integer, String, Column, DateTime, Boolean
from sqlalchemy.orm import relationship
from db.base_class import Base


class State(Base):
    __tablaname__='State'
    id=Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True) 
    created=Column(Boolean,default=True)
    send=Column(Boolean,default=False)
    open=Column(Boolean,default=False)
    acepted=Column(Boolean,default=False)
    planning=Column(Boolean,default=False)
    realized=Column(Boolean,default=False)
    timestamp_update=Column(DateTime)

    
    