
from sqlalchemy import Integer, String, Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship


from db.base_class import Base

from models.Member import Member
from models.Campaign import Campaign

from sqlalchemy import Integer, Enum




class Campaign_Member(Base):
    __tablename__='Campaign_Member'
    campaign_id=Column(Integer, ForeignKey(Campaign.id, ondelete="CASCADE"),primary_key=True)
    member_id=Column(Integer, ForeignKey(Member.id,ondelete="CASCADE"),primary_key=True)
    role=Column(Enum("WorkerBee","QueenBee","DroneBee" ),primary_key=True)

    
    # member=relationship("Member",back_populates="roles")
