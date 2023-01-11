
from sqlalchemy import Integer, String, Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship


from db.base_class import Base

from models.Member import Member
from models.Hive import Hive





class Role(Base):
    __tablename__='Role'
    hive_id=Column(Integer, ForeignKey(Hive.id, ondelete="CASCADE"),primary_key=True)
    member_id=Column(Integer, ForeignKey(Member.id,ondelete="CASCADE"),primary_key=True)
    role=Column(String,primary_key=True)
    
    
    member=relationship("Member",back_populates="roles",cascade="all, delete")
