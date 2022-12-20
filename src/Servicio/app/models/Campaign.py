
from sqlalchemy import Integer, String, Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from db.base_class import Base
#from models.Hive import Hive
from models.Hive import Hive
from models.Member import Member


class Campaign(Base):
    __tablename__='Campaign'
    hive_id=Column(Integer,ForeignKey(Hive.id),primary_key=True)
    id=Column(Integer, unique=True, primary_key=True, autoincrement=True) 
    creator_id=Column(Integer,ForeignKey(Member.id))
    city=Column(String, nullable=False)
    start_timestamp=Column(DateTime)
    # cell_edge=Column(Integer)
    min_samples=Column(Integer,default=12)
    sampling_period=Column(Integer,default=3600)
    planning_limit_time=Column(Integer, default=3600*24*2)
    campaign_duration=Column(Integer, default=3600*24*14)

    surfaces=relationship("Surface")
    # cells=relationship("Cell")


