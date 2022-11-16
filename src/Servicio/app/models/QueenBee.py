from sqlalchemy import Integer, String, Column
from sqlalchemy.orm import relationship
from db.base_class import Base


class QueenBee(Base):
    __tablaname__='QueenBee'
    id=Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True) 
    name=Column(String) 
    age=Column(Integer)
    surname=Column(String)
    city=Column(String)
    gender=Column(String,default='I dont want to answer')

    campaigns= relationship("Campaign")
    
    