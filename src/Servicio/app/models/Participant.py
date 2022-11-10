

from sqlalchemy import Integer, String, Column, Boolean, ForeignKey
from sqlalchemy.orm import relationship


from db.base_class import Base



class Participant(Base):
    __tablename__='Participant'
    id=Column(Integer, primary_key=True, index=True, unique=True,  autoincrement=True)
    name=Column(String)
    age=Column(Integer)
    surname=Column(String)
    # city=Column(String)
    gender=Column(String,default='I dont want to answer')
    
    
if __name__ == "__main__":
    a=Participant(id=1,name="hola",surname="hola",gender="Hola")
