from typing import Optional, List, Sequence, Union
from pydantic import BaseModel
from enum import Enum
from datetime import datetime, timezone



class role(str, Enum):
    WorkerBee="WorkerBee" 
    QueenBee="QueenBee" 
    BeeKeeper="BeeKeeper" 
    DroneBee="DroneBee" 
    Hive="Hive"
    
class gender_type(str, Enum):
    MALE="MALE"
    NOBINARY="NOBINARY"
    FEMALE="FEMALE"
    NOANSWER ='NOANSWER' 
    
    
    
class NewMemberBase(BaseModel):
    name: str 
    surname: str=None
    age: int
    gender: gender_type
    city: str=None
    mail:str
    real_user:bool=True
    birthday:datetime
    role: role #Union["QueenBee" or "Participant"]
 
class NewRole(BaseModel):
    role: role #Union["QueenBee" or "Participant"]

