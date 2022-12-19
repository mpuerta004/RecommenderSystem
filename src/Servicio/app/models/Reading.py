
from sqlalchemy import Integer, Column, Float
from sqlalchemy.orm import relationship
from db.base_class import Base

# sys.path.append("/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src")
# print(sys.path)


class Reading(Base):
    __tablename__='Reading'
    id=Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True,nullable=True) 
    Co2=Column(Float)
    No2=Column(Float)
    
