
from sqlalchemy import Integer, String, Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship


from db.base_class import Base

from models.Cell import Cell
from models.Participant import Participant
from models.CellMeasurement import CellMeasurement
from models.State import State



class Recommendation(Base):
    __tablename__='Recommendation'
    cell_id=Column(Integer, ForeignKey(Cell.id),primary_key=True)
    participant_id=Column(Integer, ForeignKey(Participant.id),primary_key=True)
    recommendation_timestamp=Column(DateTime,primary_key=True)
    planning_timestamp=Column(DateTime,nullable=True)
    cellMeasurement_id=Column(Integer, ForeignKey(CellMeasurement.id),nullable=True)
    state_id=Column(Integer,ForeignKey(State.id))
    
    
    state=relationship("State")
