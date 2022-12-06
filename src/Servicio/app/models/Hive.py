
from sqlalchemy import (Column, String, DateTime, Float, ForeignKey,
                        Integer)
from sqlalchemy.orm import relationship
from sqlalchemy.types import Float
from db.base_class import Base
# sys.path.append("/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src")
# print(sys.path)



class Hive(Base):
    __tablename__='Hive'
    id=Column(Integer, primary_key=True, index=True, unique=True,  autoincrement=True, nullable=False)
    city=Column(String, nullable=False)
    
    member_role=relationship("Role")
       
