
from sqlalchemy import Integer, String, Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship


from db.base_class import Base

from models.Cell import Cell
from models.Member import Member
from models.Measurement import Measurement
from models.State import State
from models.Point import Point

from models.Campaign import Campaign
from models.Slot import Slot
from models.Device import Device


class Recommendation(Base):
    __tablename__='Recommendation'
    cell_id=Column(Integer, ForeignKey(Cell.id, ondelete="CASCADE"))
    member_id=Column(Integer, ForeignKey(Member.id, ondelete="CASCADE"),primary_key=True)
    recommendation_timestamp=Column(DateTime)
    # planning_timestamp=Column(DateTime,nullable=True)
    measurement_id=Column(Integer, ForeignKey(Measurement.id, ondelete="CASCADE"),nullable=True)
    state_id=Column(Integer,ForeignKey(State.id, ondelete="CASCADE"))
    # campaign_id=Column(Integer, ForeignKey(Campaign.id))
    id=Column(Integer,primary_key=True,  autoincrement=True, nullable=False )
    member_current_location=Column(Point)
    slot_id=Column(Integer,ForeignKey(Slot.id, ondelete="CASCADE"))
    # device_id=Column(Integer, ForeignKey(Device.id, ondelete="CASCADE"))
    
    state=relationship("State",cascade="all, delete")
    cell=relationship("Cell",cascade="all, delete")
    
    
