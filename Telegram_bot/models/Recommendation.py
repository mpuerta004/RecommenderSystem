
from sqlalchemy import Integer, String, Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship


from db.base_class import Base

from models.Member import Member
# from models.State import State
from models.Point import Point

from sqlalchemy import Integer, Enum

# class State(enum.Enum):
#     NOTIFIED="NOTIFIED"
#     ACCEPTED="ACCEPTED"
#     REALIZED="REALIZED"
#     NON_REALIZED="NON_REALIZED"
from sqlalchemy import Integer, Enum, BigInteger



class Recommendation(Base):
    __tablename__='Recommendation'
    member_id=Column(BigInteger, ForeignKey(Member.id, ondelete="CASCADE"),primary_key=True)
    posicion=Column(String,nullable=False)
    id=Column(Integer,primary_key=True,  autoincrement=True, nullable=False )
    state=Column(Enum('NOTIFIED', 'ACCEPTED', 'REALIZED', 'NON_REALIZED'),nullable=False)
    
   