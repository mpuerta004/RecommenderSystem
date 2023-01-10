
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship


from db.base_class import Base
from models.Point import Point

from models.Campaign import Campaign


class Device(Base):
    __tablename__='Device'
    id=Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True) 
    
    description= Column(String, nullable=True)
    brand = Column(String, nullable=True)
    model = Column(String, nullable=True)
    year = Column(String, nullable=True)
    # measurement = relationship("Measurement")

    #De este modo se define una relacion inversa... no se si seran utiles. 
    #queenBee=relationship("Campaign", back_populates="campaigns")
    

