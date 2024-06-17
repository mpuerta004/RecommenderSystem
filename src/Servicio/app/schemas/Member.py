from typing import Optional, List, Sequence
from pydantic import BaseModel
from datetime import datetime, timezone
from enum import Enum
import numpy as np

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
    

class MemberBase(BaseModel):
    name: str =None
    surname: str=None
    age: int =None
    gender:gender_type=None
    city: str=None
    mail:str =None
    birthday:datetime =None
    real_user:bool=True
    # device_id:int=None


# Properties to receive via API on creation
class MemberCreate(MemberBase):
    pass
    

# Properties to receive via API on update
class MemberUpdate(MemberBase):
    pass


class MemberInDBBase(MemberBase):
    id: int = None
    
    class Config:
        orm_mode = True


# Additional properties to return via API
class Member(MemberInDBBase):
    pass

# Properties properties stored in DB
class MemberInDB(MemberInDBBase):
    pass


class MemberSearchResults(BaseModel):
    results: Sequence[Member]


#These are two new classes that I have created to be able to create a new role and a new member with a role
class NewRole(BaseModel):
    role: role 


class NewMembers(BaseModel):
    member: Member
    role:role
    