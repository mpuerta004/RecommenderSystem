from typing import Optional, List, Sequence, Union
from pydantic import BaseModel
from enum import Enum



class role(str, Enum):
    WorkerBee="WorkerBee" 
    QueenBee="QueenBee" 
    BeeKeeper="BeeKeeper" 
    DroneBee="DroneBee" 
    Hive="Hive"
    

class gender_type(str, Enum):
    NoBinary="NoBinary"
    Male="Male"
    Female="Female"
    IDontWantToAnser='I dont want to answer' 
   
    
    
class NewMemberBase(BaseModel):
    name: str 
    surname: str=None
    age: int
    gender: gender_type
    city: str=None
    mail:str
    real_user:bool=True
    role: role #Union["QueenBee" or "Participant"]
 
class NewRole(BaseModel):
    role: role #Union["QueenBee" or "Participant"]

