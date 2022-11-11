
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship


from db.base_class import Base

from models.Campaign import Campaign


class Surface(Base):
    __tablename__='Surface'
    id=Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True) 
    campaign_id=Column(Integer,ForeignKey(Campaign.id))
    
    
    campaigns=relationship("Campaign", back_populates="surfaces")
    cells = relationship("Cell", back_populates="surfaces_cells")

    #De este modo se define una relacion inversa... no se si seran utiles. 
    #queenBee=relationship("Campaign", back_populates="campaigns")
    

