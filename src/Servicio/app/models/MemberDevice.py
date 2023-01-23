
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship


from db.base_class import Base

from models.Device import Device
from models.Member import Member

class MemberDevice(Base):
    __tablename__='MemberDevice'
    device_id = Column(Integer,ForeignKey(Device.id, ondelete="CASCADE"))
    member_id=Column(Integer,ForeignKey(Member.id, ondelete="CASCADE"),primary_key=True)
    

