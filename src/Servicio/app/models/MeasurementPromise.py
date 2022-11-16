

from sqlalchemy import Integer, String, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship


from db.base_class import Base

from models.Cell import Cell
from models.Participant import Participant
from models.CellMeasurement import CellMeasurement
from models.State import State


class MeasurementPromise(Base):
    __tablename__='MeasurementPromise'
    cell_id=Column(Integer, ForeignKey(Cell.id),primary_key=True)
    participant_id=Column(Integer, ForeignKey(Participant.id),primary_key=True)
    promise_timestamp=Column(DateTime,primary_key=True)
    timestamp_send=Column(DateTime,nullable=True)
    cellMeasurement_id=Column(Integer, ForeignKey(CellMeasurement.id),nullable=True)
    state_id=Column(Integer,ForeignKey(State.id))
    
    
    state=relationship("State")