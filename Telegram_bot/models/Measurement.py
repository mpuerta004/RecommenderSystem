
from sqlalchemy import Integer, String, Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship


from db.base_class import Base

from models.Member import Measurement
# from models.State import State
from models.Point import Point

from sqlalchemy import Integer, Enum
from sqlalchemy import Integer, Enum, BigInteger



class Measurement(Base):
    __tablename__='Measurement'
    id=Column(Integer,primary_key=True,  autoincrement=True, nullable=False )
    location=Column(Point)
    url= Column(String,nullable=False)
    
   