
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey
from sqlalchemy.orm import relationship


from db.base_class import Base

from models.QueenBee import QueenBee



class Campaign(Base):
    __tablename__='Campaign'
    id=Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True) 
    queenBee_id=Column(Integer,ForeignKey(QueenBee.id))
    
    # queenBee=relationship("QueenBee", back_populates="campaigns")
    

