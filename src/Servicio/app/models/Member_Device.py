
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship


from db.base_class import Base

from models.Device import Device
from models.Member import Member

class Member_Device(Base):
    __tablename__='Member_Device'
    device_id = Column(Integer,ForeignKey(Device.id, ondelete="RESTRICT"))
    member_id=Column(Integer,ForeignKey(Member.id, ondelete="RESTRICT"),primary_key=True)
    

