
from sqlalchemy import Integer, String, Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship


from db.base_class import Base

from models.Member import Member
# from models.State import State
from models.Point import Point

from sqlalchemy import Integer, Enum
from sqlalchemy import Integer, Enum, BigInteger



class Last_user_position(Base):
    __tablename__='Last_user_position'
    member_id=Column(BigInteger, ForeignKey(Member.id, ondelete="CASCADE"),primary_key=True)
    location=Column(Point)
    
   