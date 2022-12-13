from typing import Optional, List, Sequence, Union
from pydantic import BaseModel
from enum import Enum, IntEnum



class role(str, Enum):
    WorkerBee="WorkerBee" 
    QueenBee="QueenBee" 
    BeeKeeper="BeeKeeper" 
    DroneBee="DroneBee" 
    

    
class NewMemberBase(BaseModel):
    name: str 
    surname: str=None
    age: int
    gender: str=None
    city: str=None
    mail:str
    #Todo: no se poner esto para hacerlo bien 
    role: role #Union["QueenBee" or "Participant"]
 
class NewRole(BaseModel):
    role: role #Union["QueenBee" or "Participant"]

