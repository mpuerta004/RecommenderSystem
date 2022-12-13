

from sqlalchemy import Integer, String, Column, Boolean, ForeignKey
from sqlalchemy.orm import relationship


from db.base_class import Base


class Member(Base):
    __tablename__='Member'
    mail=Column(String, nullable=False)
    id=Column(Integer, primary_key=True, index=True, unique=True,  autoincrement=True, nullable=False)
    name=Column(String,nullable=True)
    age=Column(Integer,nullable=True)
    surname=Column(String,nullable=True)
    city=Column(String,nullable=True)
    gender=Column(String,default='I dont want to answer')
    
    Measurements=relationship("Measurement")
    roles=relationship("Role", back_populates="member")
    campaign_creator= relationship("Campaign")

    