from typing import Optional, List, Sequence
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


# class role(str, Enum):
#     WorkerBee="WorkerBee" 
#     QueenBee="QueenBee" 
#     BeeKeeper="BeeKeeper" 
#     DroneBee="DroneBee" 
#     Hive="Hive"
    
class gender_type(str, Enum):
    MALE="MALE"
    NOBINARY="NOBINARY"
    FEMALE="FEMALE"
    NOANSER='NOANSER' 
    

class MemberBase(BaseModel):
    name: str 
    surname: str=None
    age: int
    gender:gender_type
    city: str=None
    mail:str
    birthday:datetime
    real_user:bool=True
    # device_id:int=None

# # Properties to receive via API on creation
class MemberCreate(MemberBase):
     pass
    

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

class MemberInDB(MemberInDBBase):
    pass

class MemberSearchResults(BaseModel):
    results: Sequence[Member]


# # Properties to receive via API on update
# class MemberUpdate(MemberBase):
#     pass


# class MemberInDBBase(MemberBase):
#     id: int = None
#     hive_id:int

#     class Config:
#         orm_mode = True


# # Additional properties to return via API
# class Member(MemberBase):
#     id:int
    
#     #campaigns:CampaignSearchResults
#     class Config:
#         orm_mode = True



# class MemberSearchResults(BaseModel):
#     results: Sequence[Member]