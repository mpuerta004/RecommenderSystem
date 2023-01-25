

from sqlalchemy import Integer, String, Column, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Integer, Enum

from db.base_class import Base

class BeeKeeper(Base):
    __tablename__='BeeKeeper'
    mail=Column(String, nullable=False)
    id=Column(Integer, primary_key=True, index=True, unique=True,  autoincrement=True, nullable=False)
    name=Column(String,nullable=True)
    age=Column(Integer,nullable=True)
    surname=Column(String,nullable=True)
    city=Column(String,nullable=True)
    real_user=Column(Boolean,default=True)

    gender=Column(Enum("NoBinary","Male","Female",'I dont want to answer'),nullable=False)
    
    # device_id=Column(Integer,ForeignKey(Device.id, ondelete='CASCADE'))
    # Measurements=relationship("Measurement",cascade="all, delete")
    # roles=relationship("Role", back_populates="member",cascade="all, delete")
    # campaign_creator= relationship("Campaign",cascade="all, delete")

    