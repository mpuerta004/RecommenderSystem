

from sqlalchemy import Integer, String, Column, Boolean, ForeignKey
from sqlalchemy.orm import relationship


from db.base_class import Base



class Participant(Base):
    __tablename__='Participant'
    id=Column(Integer, primary_key=True, index=True, unique=True,  autoincrement=True, nullable=False)
    name=Column(String,nullable=True)
    age=Column(Integer,nullable=True)
    surname=Column(String,nullable=True)
    city=Column(String,nullable=True)
    gender=Column(String,default='I dont want to answer')
    
    cellMeasurements=relationship("CellMeasurement")
    recommendations=relationship("Recommendation")
    promises=relationship("MeasurementPromise")

    
if __name__ == "__main__":
    a=Participant(id=1,name="hola",surname="hola",gender="Hola")