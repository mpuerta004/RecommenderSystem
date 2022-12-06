
from sqlalchemy import Integer, String, Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship


from db.base_class import Base

from models.Cell import Cell
from models.Member import Member
from models.Hive import Hive

from models.CellMeasurement import CellMeasurement
from models.State import State



class Role(Base):
    __tablename__='Role'
    hive_id=Column(Integer, ForeignKey(Hive.id),primary_key=True)
    member_id=Column(Integer, ForeignKey(Member.id),primary_key=True)
    role=Column(String,primary_key=True)
    
    
    member=relationship("Member",back_populates="roles")
