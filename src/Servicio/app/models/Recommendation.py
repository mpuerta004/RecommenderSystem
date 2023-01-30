
from sqlalchemy import Integer, String, Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship


from db.base_class import Base

from models.Cell import Cell
from models.Member import Member
# from models.State import State
from models.Point import Point
from models.Slot import Slot

from sqlalchemy import Integer, Enum

# class State(enum.Enum):
#     NOTIFIED="NOTIFIED"
#     ACCEPTED="ACCEPTED"
#     REALIZED="REALIZED"
#     NON_REALIZED="NON_REALIZED"



class Recommendation(Base):
    __tablename__='Recommendation'
    #cell_id=Column(Integer, ForeignKey(Cell.id, ondelete="CASCADE"))
    member_id=Column(Integer, ForeignKey(Member.id, ondelete="CASCADE"),primary_key=True)
    sent_datetime=Column(DateTime)
    # planning_timestamp=Column(DateTime,nullable=True)
    #measurement_id=Column(Integer, ForeignKey(Measurement.id, ondelete="CASCADE"),nullable=True)
    # campaign_id=Column(Integer, ForeignKey(Campaign.id))
    id=Column(Integer,primary_key=True,  autoincrement=True, nullable=False )
    member_current_location=Column(Point)
    slot_id=Column(Integer,ForeignKey(Slot.id, ondelete="CASCADE"))
    state=Column(Enum('NOTIFIED', 'ACCEPTED', 'REALIZED', 'NON_REALIZED'),nullable=False)
    update_datetime=Column(DateTime)
    
    
    #state=relationship("State",cascade="all, delete")
    # cell=relationship("Cell",cascade="all, delete")
    slot=relationship("Slot")
    
    
