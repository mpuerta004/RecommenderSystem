
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship


from db.base_class import Base

from models.Campaign import Campaign
from models.Boundary import Boundary


class Surface(Base):
    __tablename__='Surface'
    id=Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True) 
    campaign_id=Column(Integer,ForeignKey(Campaign.id, ondelete="CASCADE"))
    boundary_id=Column(Integer,ForeignKey(Boundary.id, ondelete="CASCADE"))
    boundary = relationship("Boundary",cascade="all, delete")

    cells = relationship("Cell",cascade="all, delete")

    

