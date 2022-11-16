
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship


from db.base_class import Base

from models.Campaign import Campaign


class Surface(Base):
    __tablename__='Surface'
    id=Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True) 
    campaign_id=Column(Integer,ForeignKey(Campaign.id))
    
    
    cells = relationship("Cell")

    #De este modo se define una relacion inversa... no se si seran utiles. 
    #queenBee=relationship("Campaign", back_populates="campaigns")
    

