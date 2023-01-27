from typing import Optional, List, Sequence
from pydantic import BaseModel
from enum import Enum
from datetime import datetime

class gender_type(str, Enum):
    Male="Male"
    NoBinary="NoBinary"
    Female="Female"
    IDontWantToAnser='I dont want to answer' 
    
    
class BeeKeeperBase(BaseModel):
    name: str 
    surname: str=None
    age: int
    gender:gender_type
    birthday:datetime
    city: str=None
    mail:str
    real_user:bool=True

    
    # device_id:int=None

# # Properties to receive via API on creation
class BeeKeeperCreate(BeeKeeperBase):
     pass
    

# Properties to receive via API on creation
class BeeKeeperCreate(BeeKeeperBase):
    pass
    



# Properties to receive via API on update
class BeeKeeperUpdate(BeeKeeperBase):
    pass


class BeeKeeperInDBBase(BeeKeeperBase):
    id: int = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class BeeKeeper(BeeKeeperInDBBase):
    id:int
   
    

class BeeKeeperInDB(BeeKeeperInDBBase):
    pass

class BeeKeeperSearchResults(BaseModel):
    results: Sequence[BeeKeeper]


# # Properties to receive via API on update
# class MemberUpdate(MemberBase):
#     pass


# class MemberInDBBase(MemberBase):
#     id: int = None
#     hive_id:int

#     class Config:
#         orm_mode = True


# # Additional properties to return via API
# class BeeKeeper(MemberBase):
#     id:int
    
#     #campaigns:CampaignSearchResults
#     class Config:
#         orm_mode = True



# class MemberSearchResults(BaseModel):
#     results: Sequence[BeeKeeper]