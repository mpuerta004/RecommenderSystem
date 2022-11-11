
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship


from db.base_class import Base

from models.QueenBee import QueenBee



class Campaign(Base):
    __tablename__='Campaign'
    id=Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True) 
    queenBee_id=Column(Integer,ForeignKey(QueenBee.id))
    start_timestamp=Column(DateTime)
    cell_edge=Column(Integer)
    min_samples=Column(Integer,default=12)
    sampling_period=Column(Integer,default=3600)
    planning_limit_time=Column(Integer, default=3600*24*2)
    campaign_duration=Column(Integer, default=3600*24*14)
    
    #Todo: esto para que sirve si no esta en la base de datos! 
    #De este modo se define una relacion inversa... no se si seran utiles. 
    queenBee=relationship("QueenBee", back_populates="campaigns")
    surfaces=relationship("Surface", back_populates="campaigns")
    #cells=relationship("Cell",back_populates="campaign")


