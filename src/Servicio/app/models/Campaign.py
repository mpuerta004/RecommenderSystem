
from sqlalchemy import Integer, String, Column, ForeignKey, DateTime,Float
from sqlalchemy.orm import relationship
from db.base_class import Base
from models.Hive import Hive
# from models.Member import Member


class Campaign(Base):
    __tablename__='Campaign'
    id=Column(Integer, primary_key=True, index=True, unique=True,  nullable=False)
    hive_id=Column(Integer,ForeignKey(Hive.id, ondelete="CASCADE"),primary_key=True)
    id=Column(Integer, unique=True, primary_key=True, autoincrement=True) 
    title=Column(String, nullable=True)
    start_datetime=Column(DateTime)
    cells_distance=Column(Float)
    min_samples=Column(Integer,default=12)
    sampling_period=Column(Integer,default=3600)
    end_datetime=Column(DateTime)
    hypothesis = Column(String ) 
    surfaces=relationship("Surface",cascade="all, delete")


